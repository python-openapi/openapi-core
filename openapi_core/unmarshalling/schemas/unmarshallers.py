import logging
from typing import Any
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Type
from typing import Union

from jsonschema_path import SchemaPath

from openapi_core.extensions.models.factories import ModelPathFactory
from openapi_core.schema.schemas import get_properties
from openapi_core.unmarshalling.schemas.datatypes import FormatUnmarshaller
from openapi_core.unmarshalling.schemas.datatypes import (
    FormatUnmarshallersDict,
)
from openapi_core.validation.schemas.validators import SchemaValidator

log = logging.getLogger(__name__)


class PrimitiveUnmarshaller:
    def __init__(
        self,
        schema: SchemaPath,
        schema_validator: SchemaValidator,
        schema_unmarshaller: "SchemaUnmarshaller",
    ) -> None:
        self.schema = schema
        self.schema_validator = schema_validator
        self.schema_unmarshaller = schema_unmarshaller

    def __call__(self, value: Any) -> Any:
        return value


class ArrayUnmarshaller(PrimitiveUnmarshaller):
    def __call__(self, value: Any) -> Optional[List[Any]]:
        return list(map(self.items_unmarshaller.unmarshal, value))

    @property
    def items_unmarshaller(self) -> "SchemaUnmarshaller":
        # sometimes we don't have any schema i.e. free-form objects
        items_schema = self.schema.get("items", SchemaPath.from_dict({}))
        return self.schema_unmarshaller.evolve(items_schema)


class ObjectUnmarshaller(PrimitiveUnmarshaller):
    def __call__(self, value: Any) -> Any:
        properties = self._unmarshal_properties(value)

        fields: Iterable[str] = properties and properties.keys() or []
        object_class = self.object_class_factory.create(self.schema, fields)

        return object_class(**properties)

    @property
    def object_class_factory(self) -> ModelPathFactory:
        return ModelPathFactory()

    def evolve(self, schema: SchemaPath) -> "ObjectUnmarshaller":
        cls = self.__class__

        return cls(
            schema,
            self.schema_validator.evolve(schema),
            self.schema_unmarshaller,
        )

    def _unmarshal_properties(
        self, value: Any, schema_only: bool = False
    ) -> Any:
        properties = {}

        one_of_schema = self.schema_validator.get_one_of_schema(value)
        if one_of_schema is not None:
            one_of_properties = self.evolve(
                one_of_schema
            )._unmarshal_properties(value, schema_only=True)
            properties.update(one_of_properties)

        any_of_schemas = self.schema_validator.iter_any_of_schemas(value)
        for any_of_schema in any_of_schemas:
            any_of_properties = self.evolve(
                any_of_schema
            )._unmarshal_properties(value, schema_only=True)
            properties.update(any_of_properties)

        all_of_schemas = self.schema_validator.iter_all_of_schemas(value)
        for all_of_schema in all_of_schemas:
            all_of_properties = self.evolve(
                all_of_schema
            )._unmarshal_properties(value, schema_only=True)
            properties.update(all_of_properties)

        for prop_name, prop_schema in get_properties(self.schema).items():
            try:
                prop_value = value[prop_name]
            except KeyError:
                if "default" not in prop_schema:
                    continue
                prop_value = prop_schema["default"]

            properties[prop_name] = self.schema_unmarshaller.evolve(
                prop_schema
            ).unmarshal(prop_value)

        if schema_only:
            return properties

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
            additional_prop_unmarshaler = self.schema_unmarshaller.evolve(
                additional_prop_schema
            )
            for prop_name, prop_value in value.items():
                if prop_name in properties:
                    continue
                properties[prop_name] = additional_prop_unmarshaler.unmarshal(
                    prop_value
                )

        return properties


class MultiTypeUnmarshaller(PrimitiveUnmarshaller):
    def __call__(self, value: Any) -> Any:
        primitive_type = self.schema_validator.get_primitive_type(value)
        # OpenAPI 3.0: handle no type for None
        if primitive_type is None:
            return None
        unmarshaller = self.schema_unmarshaller.get_type_unmarshaller(
            primitive_type
        )
        return unmarshaller(value)


class AnyUnmarshaller(MultiTypeUnmarshaller):
    pass


class TypesUnmarshaller:
    unmarshallers: Mapping[str, Type[PrimitiveUnmarshaller]] = {}
    multi: Optional[Type[PrimitiveUnmarshaller]] = None

    def __init__(
        self,
        unmarshallers: Mapping[str, Type[PrimitiveUnmarshaller]],
        default: Type[PrimitiveUnmarshaller],
        multi: Optional[Type[PrimitiveUnmarshaller]] = None,
    ):
        self.unmarshallers = unmarshallers
        self.default = default
        self.multi = multi

    def get_types(self) -> List[str]:
        return list(self.unmarshallers.keys())

    def get_unmarshaller_cls(
        self,
        schema_type: Optional[Union[Iterable[str], str]],
    ) -> Type["PrimitiveUnmarshaller"]:
        if schema_type is None:
            return self.default
        if isinstance(schema_type, Iterable) and not isinstance(
            schema_type, str
        ):
            if self.multi is None:
                raise TypeError("Unmarshaller does not accept multiple types")
            return self.multi

        return self.unmarshallers[schema_type]


class FormatsUnmarshaller:
    def __init__(
        self,
        format_unmarshallers: Optional[FormatUnmarshallersDict] = None,
        extra_format_unmarshallers: Optional[FormatUnmarshallersDict] = None,
    ):
        if format_unmarshallers is None:
            format_unmarshallers = {}
        self.format_unmarshallers = format_unmarshallers
        if extra_format_unmarshallers is None:
            extra_format_unmarshallers = {}
        self.extra_format_unmarshallers = extra_format_unmarshallers

    def unmarshal(self, schema_format: str, value: Any) -> Any:
        format_unmarshaller = self.get_unmarshaller(schema_format)
        if format_unmarshaller is None:
            return value
        try:
            return format_unmarshaller(value)
        except (AttributeError, ValueError, TypeError):
            return value

    def get_unmarshaller(
        self, schema_format: str
    ) -> Optional[FormatUnmarshaller]:
        if schema_format in self.extra_format_unmarshallers:
            return self.extra_format_unmarshallers[schema_format]
        if schema_format in self.format_unmarshallers:
            return self.format_unmarshallers[schema_format]

        return None

    def __contains__(self, schema_format: str) -> bool:
        format_unmarshallers_dicts: List[Mapping[str, Any]] = [
            self.extra_format_unmarshallers,
            self.format_unmarshallers,
        ]
        for content in format_unmarshallers_dicts:
            if schema_format in content:
                return True
        return False


class SchemaUnmarshaller:
    def __init__(
        self,
        schema: SchemaPath,
        schema_validator: SchemaValidator,
        types_unmarshaller: TypesUnmarshaller,
        formats_unmarshaller: FormatsUnmarshaller,
    ):
        self.schema = schema
        self.schema_validator = schema_validator

        self.types_unmarshaller = types_unmarshaller
        self.formats_unmarshaller = formats_unmarshaller

    def unmarshal(self, value: Any) -> Any:
        self.schema_validator.validate(value)

        # skip unmarshalling for nullable in OpenAPI 3.0
        if value is None and self.schema.getkey("nullable", False):
            return value

        schema_type = self.schema.getkey("type")
        type_unmarshaller = self.get_type_unmarshaller(schema_type)
        typed = type_unmarshaller(value)
        # skip finding format for None
        if typed is None:
            return None
        schema_format = self.find_format(value)
        if schema_format is None:
            return typed
        # ignore incompatible formats
        if not (
            isinstance(value, str)
            or
            # Workaround allows bytes for binary and byte formats
            (isinstance(value, bytes) and schema_format in ["binary", "byte"])
        ):
            return typed

        format_unmarshaller = self.get_format_unmarshaller(schema_format)
        if format_unmarshaller is None:
            return typed
        try:
            return format_unmarshaller(typed)
        except (AttributeError, ValueError, TypeError):
            return typed

    def get_type_unmarshaller(
        self,
        schema_type: Optional[Union[Iterable[str], str]],
    ) -> PrimitiveUnmarshaller:
        klass = self.types_unmarshaller.get_unmarshaller_cls(schema_type)
        return klass(
            self.schema,
            self.schema_validator,
            self,
        )

    def get_format_unmarshaller(
        self,
        schema_format: str,
    ) -> Optional[FormatUnmarshaller]:
        return self.formats_unmarshaller.get_unmarshaller(schema_format)

    def evolve(self, schema: SchemaPath) -> "SchemaUnmarshaller":
        cls = self.__class__

        return cls(
            schema,
            self.schema_validator.evolve(schema),
            self.types_unmarshaller,
            self.formats_unmarshaller,
        )

    def find_format(self, value: Any) -> Optional[str]:
        for schema in self.schema_validator.iter_valid_schemas(value):
            schema_validator = self.schema_validator.evolve(schema)
            primitive_type = schema_validator.get_primitive_type(value)
            if primitive_type != "string":
                continue
            if "format" in schema:
                return str(schema.getkey("format"))
        return None
