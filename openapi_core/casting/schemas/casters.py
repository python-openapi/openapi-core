from typing import Any
from typing import Generic
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.schema.schemas import get_properties
from openapi_core.util import BOOLEAN_FALSE_VALUES
from openapi_core.util import BOOLEAN_TRUE_VALUES
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

    def __call__(self, value: Any) -> Any:
        self.validate(value)

        return self.cast(value)

    def validate(self, value: Any) -> None:
        pass

    def cast(self, value: Any) -> Any:
        return value


PrimitiveType = TypeVar("PrimitiveType")


class PrimitiveTypeCaster(Generic[PrimitiveType], PrimitiveCaster):
    primitive_type: Type[PrimitiveType] = NotImplemented

    def cast(self, value: Union[str, bytes]) -> PrimitiveType:
        return self.primitive_type(value)  # type: ignore [call-arg]


class IntegerCaster(PrimitiveTypeCaster[int]):
    primitive_type = int


class NumberCaster(PrimitiveTypeCaster[float]):
    primitive_type = float


class BooleanCaster(PrimitiveTypeCaster[bool]):
    primitive_type = bool

    def validate(self, value: Any) -> None:
        super().validate(value)

        if isinstance(value, bool):
            return

        if value.lower() not in BOOLEAN_TRUE_VALUES + BOOLEAN_FALSE_VALUES:
            raise ValueError("not a boolean format")

    def cast(self, value: Union[str, bytes]) -> bool:
        return self.primitive_type(forcebool(value))


class ArrayCaster(PrimitiveCaster):
    @property
    def items_caster(self) -> "SchemaCaster":
        # sometimes we don't have any schema i.e. free-form objects
        items_schema = self.schema.get("items", SchemaPath.from_dict({}))
        return self.schema_caster.evolve(items_schema)

    def validate(self, value: Any) -> None:
        # str and bytes are not arrays according to the OpenAPI spec
        if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
            raise ValueError("not an array format")

    def cast(self, value: list[Any]) -> list[Any]:
        return list(map(self.items_caster.cast, value))


class ObjectCaster(PrimitiveCaster):
    def validate(self, value: Any) -> None:
        if not isinstance(value, dict):
            raise ValueError("not an object format")

    def cast(self, value: dict[str, Any]) -> dict[str, Any]:
        return self._cast_proparties(value)

    def evolve(self, schema: SchemaPath) -> "ObjectCaster":
        cls = self.__class__

        return cls(
            schema,
            self.schema_validator.evolve(schema),
            self.schema_caster.evolve(schema),
        )

    def _cast_proparties(
        self, value: dict[str, Any], schema_only: bool = False
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("not an object format")

        all_of_schemas = self.schema_validator.iter_all_of_schemas(value)
        for all_of_schema in all_of_schemas:
            all_of_properties = self.evolve(all_of_schema)._cast_proparties(
                value, schema_only=True
            )
            value.update(all_of_properties)

        for prop_name, prop_schema in get_properties(self.schema).items():
            try:
                prop_value = value[prop_name]
            except KeyError:
                continue
            value[prop_name] = self.schema_caster.evolve(prop_schema).cast(
                prop_value
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
                value[prop_name] = additional_prop_caster.cast(prop_value)

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

    def cast(self, value: Any) -> Any:
        # skip casting for nullable in OpenAPI 3.0
        if value is None and self.schema.getkey("nullable", False):
            return value

        schema_type = self.schema.getkey("type")

        type_caster = self.get_type_caster(schema_type)

        if value is None:
            return value

        try:
            return type_caster(value)
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
