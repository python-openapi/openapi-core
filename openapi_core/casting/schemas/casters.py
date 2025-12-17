from typing import Any
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.media_types.enums import DataKind
from openapi_core.schema.schemas import get_properties
from openapi_core.util import forcebool
from openapi_core.validation.schemas.validators import SchemaValidator


class PrimitiveCaster:
    def __init__(
        self,
        schema: SchemaPath,
        schema_validator: SchemaValidator,
        schema_caster: "SchemaCaster",
    ):
        self.schema = schema
        self.schema_validator = schema_validator
        self.schema_caster = schema_caster

    def __call__(
        self,
        value: Any,
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> Any:
        return value


PrimitiveType = TypeVar("PrimitiveType")


class PrimitiveTypeCaster(Generic[PrimitiveType], PrimitiveCaster):
    primitive_type: Type[PrimitiveType] = NotImplemented

    def __call__(
        self,
        value: Union[str, bytes],
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> Any:
        # STRINGLY: only coerce from str/bytes, return others unchanged
        if data_kind == DataKind.STRINGLY:
            if not isinstance(value, (str, bytes)):
                return value

        self.validate(value)

        return self.primitive_type(value)  # type: ignore [call-arg]

    def validate(self, value: Any) -> None:
        pass


class IntegerCaster(PrimitiveTypeCaster[int]):
    primitive_type = int


class NumberCaster(PrimitiveTypeCaster[float]):
    primitive_type = float


class BooleanCaster(PrimitiveTypeCaster[bool]):
    primitive_type = bool

    def __call__(
        self,
        value: Union[str, bytes],
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> Any:
        # STRINGLY: only coerce from str/bytes, return others unchanged
        if data_kind == DataKind.STRINGLY:
            if not isinstance(value, (str, bytes)):
                return value

        self.validate(value)

        return self.primitive_type(forcebool(value))

    def validate(self, value: Any) -> None:
        # Already a boolean, accept it
        if isinstance(value, bool):
            return

        if not isinstance(value, (str, bytes)):
            return

        if value.lower() not in ["false", "true"]:
            raise ValueError("not a boolean format")


class ArrayCaster(PrimitiveCaster):
    @property
    def items_caster(self) -> "SchemaCaster":
        # sometimes we don't have any schema i.e. free-form objects
        items_schema = self.schema.get("items", SchemaPath.from_dict({}))
        return self.schema_caster.evolve(items_schema)

    def __call__(
        self,
        value: Any,
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> List[Any]:
        # str and bytes are not arrays according to the OpenAPI spec
        if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
            raise CastError(value, self.schema["type"])

        # Array items don't have property names, pass empty data kinds dict
        try:
            return list(
                map(
                    lambda item: self.items_caster.cast(
                        item, data_kind=data_kind, property_data_kinds={}
                    ),
                    value,
                )
            )
        except (ValueError, TypeError):
            raise CastError(value, self.schema["type"])


class ObjectCaster(PrimitiveCaster):
    def __call__(
        self,
        value: Any,
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> Any:
        return self._cast_proparties(
            value,
            schema_only=False,
            data_kind=data_kind,
            property_data_kinds=property_data_kinds or {},
        )

    def evolve(self, schema: SchemaPath) -> "ObjectCaster":
        cls = self.__class__

        return cls(
            schema,
            self.schema_validator.evolve(schema),
            self.schema_caster.evolve(schema),
        )

    def _cast_proparties(
        self,
        value: Any,
        schema_only: bool = False,
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> Any:
        if not isinstance(value, dict):
            raise CastError(value, self.schema["type"])

        if property_data_kinds is None:
            property_data_kinds = {}

        all_of_schemas = self.schema_validator.iter_all_of_schemas(value)
        for all_of_schema in all_of_schemas:
            all_of_properties = self.evolve(all_of_schema)._cast_proparties(
                value,
                schema_only=True,
                data_kind=data_kind,
                property_data_kinds=property_data_kinds,
            )
            value.update(all_of_properties)

        for prop_name, prop_schema in get_properties(self.schema).items():
            try:
                prop_value = value[prop_name]
            except KeyError:
                continue

            # Use property-specific data kind if available, otherwise inherit parent data kind
            prop_data_kind = property_data_kinds.get(prop_name, data_kind)

            value[prop_name] = self.schema_caster.evolve(prop_schema).cast(
                prop_value,
                data_kind=prop_data_kind,
                property_data_kinds={},  # Data kinds don't cascade to nested objects
            )

        if schema_only:
            return value

        additional_properties = self.schema.getkey(
            "additionalProperties", True
        )
        if additional_properties is not False:
            # free-form object
            if additional_properties is True:
                additional_prop_schema = SchemaPath.from_dict(
                    {"nullable": True}
                )
            # defined schema
            else:
                additional_prop_schema = self.schema / "additionalProperties"
            additional_prop_caster = self.schema_caster.evolve(
                additional_prop_schema
            )
            for prop_name, prop_value in value.items():
                if prop_name in value:
                    continue
                value[prop_name] = additional_prop_caster.cast(
                    prop_value, data_kind=data_kind
                )

        return value


class TypesCaster:
    casters: Mapping[str, Type[PrimitiveCaster]] = {}
    multi: Optional[Type[PrimitiveCaster]] = None

    def __init__(
        self,
        casters: Mapping[str, Type[PrimitiveCaster]],
        default: Type[PrimitiveCaster],
        multi: Optional[Type[PrimitiveCaster]] = None,
    ):
        self.casters = casters
        self.default = default
        self.multi = multi

    def get_caster(
        self,
        schema_type: Optional[Union[Iterable[str], str]],
    ) -> Type["PrimitiveCaster"]:
        if schema_type is None:
            return self.default
        if isinstance(schema_type, Iterable) and not isinstance(
            schema_type, str
        ):
            if self.multi is None:
                raise TypeError("caster does not accept multiple types")
            return self.multi

        return self.casters[schema_type]


class SchemaCaster:
    def __init__(
        self,
        schema: SchemaPath,
        schema_validator: SchemaValidator,
        types_caster: TypesCaster,
    ):
        self.schema = schema
        self.schema_validator = schema_validator

        self.types_caster = types_caster

    def cast(
        self,
        value: Any,
        data_kind: DataKind = DataKind.STRINGLY,
        property_data_kinds: Optional[Dict[str, DataKind]] = None,
    ) -> Any:
        # TYPED data: return value unchanged, no casting applied
        if data_kind == DataKind.TYPED:
            return value

        # skip casting for nullable in OpenAPI 3.0
        if value is None and self.schema.getkey("nullable", False):
            return value

        schema_type = self.schema.getkey("type")

        type_caster = self.get_type_caster(schema_type)

        if value is None:
            return value

        try:
            return type_caster(
                value,
                data_kind=data_kind,
                property_data_kinds=property_data_kinds,
            )
        except (ValueError, TypeError):
            raise CastError(value, schema_type)

    def get_type_caster(
        self,
        schema_type: Optional[Union[Iterable[str], str]],
    ) -> PrimitiveCaster:
        caster_cls = self.types_caster.get_caster(schema_type)
        return caster_cls(
            self.schema,
            self.schema_validator,
            self,
        )

    def evolve(self, schema: SchemaPath) -> "SchemaCaster":
        cls = self.__class__

        return cls(
            schema,
            self.schema_validator.evolve(schema),
            self.types_caster,
        )
