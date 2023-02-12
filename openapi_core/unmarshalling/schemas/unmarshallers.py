import logging
import warnings
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional
from typing import Type
from typing import Union
from typing import cast

from openapi_core.extensions.models.factories import ModelPathFactory
from openapi_core.schema.schemas import get_properties
from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.enums import ValidationContext
from openapi_core.unmarshalling.schemas.exceptions import FormatUnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import UnmarshallerError
from openapi_core.validation.schemas.exceptions import ValidateError
from openapi_core.validation.schemas.validators import SchemaValidator

if TYPE_CHECKING:
    from openapi_core.unmarshalling.schemas.factories import (
        SchemaFormatUnmarshallersFactory,
    )
    from openapi_core.unmarshalling.schemas.factories import (
        SchemaUnmarshallersFactory,
    )
    from openapi_core.unmarshalling.schemas.factories import (
        SchemaValidatorsFactory,
    )

log = logging.getLogger(__name__)


class PrimitiveUnmarshaller:
    def __init__(
        self,
        schema,
        schema_validator,
        schema_unmarshaller,
        schema_unmarshallers_factory,
    ) -> None:
        self.schema = schema
        self.schema_validator = schema_validator
        self.schema_unmarshaller = schema_unmarshaller
        self.schema_unmarshallers_factory = schema_unmarshallers_factory

        self.schema_format = schema.getkey("format")

    def __call__(self, value: Any, subschemas: bool = True) -> Any:
        best_format = self._get_format(value, subschemas=subschemas)
        format_unmarshaller = self.schema_unmarshallers_factory.format_unmarshallers_factory.create(
            best_format
        )
        if format_unmarshaller is None:
            return value
        try:
            return format_unmarshaller(value)
        except (ValueError, TypeError) as exc:
            raise FormatUnmarshalError(value, self.schema_format, exc)

    def _get_format(
        self, value: Any, subschemas: bool = True
    ) -> Optional[str]:
        if "format" in self.schema:
            return self.schema.getkey("format")

        if subschemas is False:
            return None

        one_of_schema = self.schema_validator.get_one_of_schema(value)
        if one_of_schema is not None and "format" in one_of_schema:
            return one_of_schema.getkey("format")

        any_of_schemas = self.schema_validator.iter_any_of_schemas(value)
        for any_of_schema in any_of_schemas:
            if "format" in any_of_schema:
                return any_of_schema.getkey("format")

        all_of_schemas = self.schema_validator.iter_all_of_schemas(value)
        for all_of_schema in all_of_schemas:
            if "format" in all_of_schema:
                return all_of_schema.getkey("format")

        return None


class ArrayUnmarshaller(PrimitiveUnmarshaller):
    @property
    def items_unmarshaller(self) -> "PrimitiveUnmarshaller":
        # sometimes we don't have any schema i.e. free-form objects
        items_schema = self.schema.get(
            "items", Spec.from_dict({}, validator=None)
        )
        return self.schema_unmarshaller.evolve(items_schema)

    def __call__(self, value: Any) -> Optional[List[Any]]:
        return list(map(self.items_unmarshaller.unmarshal, value))


class ObjectUnmarshaller(PrimitiveUnmarshaller):
    context = NotImplemented

    @property
    def object_class_factory(self) -> ModelPathFactory:
        return ModelPathFactory()

    def __call__(self, value: Any) -> Any:
        properties = self._unmarshal_raw(value)

        fields: Iterable[str] = properties and properties.keys() or []
        object_class = self.object_class_factory.create(self.schema, fields)

        return object_class(**properties)

    def _unmarshal_raw(self, value: Any, schema_only: bool = False) -> Any:
        formatted = super().__call__(value)
        return self._unmarshal_properties(formatted, schema_only=schema_only)

    def evolve(self, schema: Spec) -> "ObjectUnmarshaller":
        return self.schema_unmarshaller.evolve(schema).get_unmarshaller(
            "object"
        )

    def _unmarshal_properties(
        self, value: Any, schema_only: bool = False
    ) -> Any:
        properties = {}

        one_of_schema = self.schema_validator.get_one_of_schema(value)
        if one_of_schema is not None:
            one_of_properties = self.evolve(one_of_schema)._unmarshal_raw(
                value, schema_only=True
            )
            properties.update(one_of_properties)

        any_of_schemas = self.schema_validator.iter_any_of_schemas(value)
        for any_of_schema in any_of_schemas:
            any_of_properties = self.evolve(any_of_schema)._unmarshal_raw(
                value, schema_only=True
            )
            properties.update(any_of_properties)

        all_of_schemas = self.schema_validator.iter_all_of_schemas(value)
        for all_of_schema in all_of_schemas:
            all_of_properties = self.evolve(all_of_schema)._unmarshal_raw(
                value, schema_only=True
            )
            properties.update(all_of_properties)

        for prop_name, prop_schema in get_properties(self.schema).items():
            # check for context in OpenAPI 3.0
            if self.context is not NotImplemented:
                read_only = prop_schema.getkey("readOnly", False)
                if self.context == ValidationContext.REQUEST and read_only:
                    continue
                write_only = prop_schema.getkey("writeOnly", False)
                if self.context == ValidationContext.RESPONSE and write_only:
                    continue
            try:
                prop_value = value[prop_name]
            except KeyError:
                if "default" not in prop_schema:
                    continue
                prop_value = prop_schema["default"]

            properties[prop_name] = self.schema_unmarshallers_factory.create(
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
                additional_prop_schema = Spec.from_dict(
                    {"nullable": True}, validator=None
                )
            # defined schema
            else:
                additional_prop_schema = self.schema / "additionalProperties"
            additional_prop_unmarshaler = (
                self.schema_unmarshallers_factory.create(
                    additional_prop_schema
                )
            )
            for prop_name, prop_value in value.items():
                if prop_name in properties:
                    continue
                properties[prop_name] = additional_prop_unmarshaler.unmarshal(
                    prop_value
                )

        return properties


class ObjectReadUnmarshaller(ObjectUnmarshaller):
    context = ValidationContext.RESPONSE


class ObjectWriteUnmarshaller(ObjectUnmarshaller):
    context = ValidationContext.REQUEST


class MultiTypeUnmarshaller(PrimitiveUnmarshaller):
    @property
    def type(self) -> List[str]:
        types = self.schema.getkey("type", ["any"])
        assert isinstance(types, list)
        return types

    def _get_best_unmarshaller(self, value: Any) -> "PrimitiveUnmarshaller":
        for schema_type in self.type:
            result = self.schema_validator.type_validator(
                value, type_override=schema_type
            )
            if not result:
                continue
            result = self.schema_validator.format_validator(value)
            if not result:
                continue
            return self.schema_unmarshaller.get_unmarshaller(schema_type)

        raise UnmarshallerError("Unmarshaller not found for type(s)")

    def __call__(self, value: Any) -> Any:
        unmarshaller = self._get_best_unmarshaller(value)
        return unmarshaller(value)


class AnyUnmarshaller(MultiTypeUnmarshaller):
    SCHEMA_TYPES_ORDER = [
        "object",
        "array",
        "boolean",
        "integer",
        "number",
        "string",
    ]

    @property
    def type(self) -> List[str]:
        return self.SCHEMA_TYPES_ORDER


class TypesUnmarshaller:
    unmarshallers: Mapping[str, Type[PrimitiveUnmarshaller]] = {}
    multi: Optional[Type[PrimitiveUnmarshaller]] = None

    def __init__(
        self,
        unmarshallers: Mapping[str, Type[PrimitiveUnmarshaller]],
        default: Type[PrimitiveUnmarshaller],
        multi: bool = False,
    ):
        self.unmarshallers = unmarshallers
        self.default = default
        self.multi = multi

    def get_type_unmarshaller(
        self,
        schema_type: Optional[Union[Iterable, str]],
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


class SchemaUnmarshaller:
    def __init__(
        self,
        schema: Spec,
        schema_validator: SchemaValidator,
        schema_unmarshallers_factory: "SchemaUnmarshallersFactory",
        format_unmarshallers_factory: "SchemaFormatUnmarshallersFactory",
        types_unmarshaller: TypesUnmarshaller,
    ):
        self.schema = schema
        self.schema_validator = schema_validator

        self.schema_unmarshallers_factory = schema_unmarshallers_factory
        self.format_unmarshallers_factory = format_unmarshallers_factory

        self.types_unmarshaller = types_unmarshaller

    def __call__(self, value: Any) -> Any:
        warnings.warn(
            "Calling unmarshaller itself is deprecated. "
            "Use unmarshal method instead.",
            DeprecationWarning,
        )
        return self.unmarshal(value)

    def unmarshal(self, value: Any, subschemas: bool = True) -> Any:
        self.schema_validator.validate(value)

        # skip unmarshalling for nullable in OpenAPI 3.0
        if value is None and self.schema.getkey("nullable", False):
            return value

        schema_type = self.schema.getkey("type")
        unmarshaller = self.get_unmarshaller(schema_type)
        return unmarshaller(value)

    def get_unmarshaller(
        self,
        schema_type: Optional[Union[Iterable, str]],
    ):
        klass = self.types_unmarshaller.get_type_unmarshaller(schema_type)
        return klass(
            self.schema,
            self.schema_validator,
            self,
            self.schema_unmarshallers_factory,
        )

    def evolve(self, schema: Spec) -> "SchemaUnmarshaller":
        cls = self.__class__

        return cls(
            schema,
            self.schema_validator.evolve(schema),
            self.schema_unmarshallers_factory,
            self.format_unmarshallers_factory,
            self.types_unmarshaller,
        )
