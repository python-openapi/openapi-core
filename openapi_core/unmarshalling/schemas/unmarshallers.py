import logging
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import cast

from isodate.isodatetime import parse_datetime
from jsonschema._types import is_array
from jsonschema._types import is_bool
from jsonschema._types import is_integer
from jsonschema._types import is_null
from jsonschema._types import is_number
from jsonschema._types import is_object
from jsonschema.protocols import Validator
from openapi_schema_validator._format import oas30_format_checker
from openapi_schema_validator._types import is_string

from openapi_core.extensions.models.factories import ModelPathFactory
from openapi_core.schema.schemas import get_all_properties
from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.datatypes import FormattersDict
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaFormatValue,
)
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import UnmarshallerError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.util import format_byte
from openapi_core.unmarshalling.schemas.util import format_date
from openapi_core.unmarshalling.schemas.util import format_number
from openapi_core.unmarshalling.schemas.util import format_uuid
from openapi_core.util import forcebool

if TYPE_CHECKING:
    from openapi_core.unmarshalling.schemas.factories import (
        SchemaUnmarshallersFactory,
    )

log = logging.getLogger(__name__)


class BaseSchemaUnmarshaller:

    FORMATTERS: FormattersDict = {
        None: Formatter(),
    }

    def __init__(
        self,
        schema: Spec,
        validator: Validator,
        formatter: Optional[Formatter],
    ):
        self.schema = schema
        self.validator = validator
        self.schema_format = schema.getkey("format")

        if formatter is None:
            if self.schema_format not in self.FORMATTERS:
                raise FormatterNotFoundError(self.schema_format)
            self.formatter = self.FORMATTERS[self.schema_format]
        else:
            self.formatter = formatter

    def __call__(self, value: Any) -> Any:
        self.validate(value)

        # skip unmarshalling for nullable in OpenAPI 3.0
        if value is None and self.schema.getkey("nullable", False):
            return value

        return self.unmarshal(value)

    def _validate_format(self, value: Any) -> None:
        result = self.formatter.validate(value)
        if not result:
            schema_type = self.schema.getkey("type", "any")
            raise InvalidSchemaValue(value, schema_type)

    def validate(self, value: Any) -> None:
        errors_iter = self.validator.iter_errors(value)
        errors = tuple(errors_iter)
        if errors:
            schema_type = self.schema.getkey("type", "any")
            raise InvalidSchemaValue(value, schema_type, schema_errors=errors)

    def format(self, value: Any) -> Any:
        try:
            return self.formatter.format(value)
        except (ValueError, TypeError) as exc:
            raise InvalidSchemaFormatValue(value, self.schema_format, exc)

    def unmarshal(self, value: Any) -> Any:
        return self.format(value)


class StringUnmarshaller(BaseSchemaUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(partial(is_string, None), str),
        "password": Formatter.from_callables(
            partial(oas30_format_checker.check, format="password"), str
        ),
        "date": Formatter.from_callables(
            partial(oas30_format_checker.check, format="date"), format_date
        ),
        "date-time": Formatter.from_callables(
            partial(oas30_format_checker.check, format="date-time"),
            parse_datetime,
        ),
        "binary": Formatter.from_callables(
            partial(oas30_format_checker.check, format="binary"), bytes
        ),
        "uuid": Formatter.from_callables(
            partial(oas30_format_checker.check, format="uuid"), format_uuid
        ),
        "byte": Formatter.from_callables(
            partial(oas30_format_checker.check, format="byte"), format_byte
        ),
    }


class IntegerUnmarshaller(BaseSchemaUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(partial(is_integer, None), int),
        "int32": Formatter.from_callables(
            partial(oas30_format_checker.check, format="int32"), int
        ),
        "int64": Formatter.from_callables(
            partial(oas30_format_checker.check, format="int64"), int
        ),
    }


class NumberUnmarshaller(BaseSchemaUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(
            partial(is_number, None), format_number
        ),
        "float": Formatter.from_callables(
            partial(oas30_format_checker.check, format="float"), float
        ),
        "double": Formatter.from_callables(
            partial(oas30_format_checker.check, format="double"), float
        ),
    }


class BooleanUnmarshaller(BaseSchemaUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(partial(is_bool, None), forcebool),
    }


class NullUnmarshaller(BaseSchemaUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(partial(is_null, None), None),
    }


class ComplexUnmarshaller(BaseSchemaUnmarshaller):
    def __init__(
        self,
        schema: Spec,
        validator: Validator,
        formatter: Optional[Formatter],
        unmarshallers_factory: "SchemaUnmarshallersFactory",
        context: Optional[UnmarshalContext] = None,
    ):
        super().__init__(schema, validator, formatter)
        self.unmarshallers_factory = unmarshallers_factory
        self.context = context


class ArrayUnmarshaller(ComplexUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(partial(is_array, None), list),
    }

    @property
    def items_unmarshaller(self) -> "BaseSchemaUnmarshaller":
        # sometimes we don't have any schema i.e. free-form objects
        items_schema = self.schema.get("items", Spec.from_dict({}))
        return self.unmarshallers_factory.create(items_schema)

    def unmarshal(self, value: Any) -> Optional[List[Any]]:
        value = super().unmarshal(value)
        return list(map(self.items_unmarshaller, value))


class ObjectUnmarshaller(ComplexUnmarshaller):

    FORMATTERS: FormattersDict = {
        None: Formatter.from_callables(partial(is_object, None), dict),
    }

    @property
    def object_class_factory(self) -> ModelPathFactory:
        return ModelPathFactory()

    def unmarshal(self, value: Any) -> Any:
        properties = self.format(value)

        fields: Iterable[str] = properties and properties.keys() or []
        object_class = self.object_class_factory.create(self.schema, fields)

        return object_class(**properties)

    def format(self, value: Any) -> Any:
        formatted = super().format(value)
        return self._unmarshal_properties(formatted)

    def _clone(self, schema: Spec) -> "ObjectUnmarshaller":
        return cast(
            "ObjectUnmarshaller",
            self.unmarshallers_factory.create(schema, "object"),
        )

    def _unmarshal_properties(self, value: Any) -> Any:
        properties = {}

        if "oneOf" in self.schema:
            one_of_properties = None
            for one_of_schema in self.schema / "oneOf":
                try:
                    unmarshalled = self._clone(one_of_schema).format(value)
                except (UnmarshalError, ValueError):
                    pass
                else:
                    if one_of_properties is not None:
                        log.warning("multiple valid oneOf schemas found")
                        continue
                    one_of_properties = unmarshalled

            if one_of_properties is None:
                log.warning("valid oneOf schema not found")
            else:
                properties.update(one_of_properties)

        elif "anyOf" in self.schema:
            any_of_properties = None
            for any_of_schema in self.schema / "anyOf":
                try:
                    unmarshalled = self._clone(any_of_schema).format(value)
                except (UnmarshalError, ValueError):
                    pass
                else:
                    any_of_properties = unmarshalled
                    break

            if any_of_properties is None:
                log.warning("valid anyOf schema not found")
            else:
                properties.update(any_of_properties)

        for prop_name, prop in get_all_properties(self.schema).items():
            read_only = prop.getkey("readOnly", False)
            if self.context == UnmarshalContext.REQUEST and read_only:
                continue
            write_only = prop.getkey("writeOnly", False)
            if self.context == UnmarshalContext.RESPONSE and write_only:
                continue
            try:
                prop_value = value[prop_name]
            except KeyError:
                if "default" not in prop:
                    continue
                prop_value = prop["default"]

            properties[prop_name] = self.unmarshallers_factory.create(prop)(
                prop_value
            )

        additional_properties = self.schema.getkey(
            "additionalProperties", True
        )
        if additional_properties is not False:
            # free-form object
            if additional_properties is True:
                additional_prop_schema = Spec.from_dict({})
            # defined schema
            else:
                additional_prop_schema = self.schema / "additionalProperties"
            additional_prop_unmarshaler = self.unmarshallers_factory.create(
                additional_prop_schema
            )
            for prop_name, prop_value in value.items():
                if prop_name in properties:
                    continue
                properties[prop_name] = additional_prop_unmarshaler(prop_value)

        return properties


class MultiTypeUnmarshaller(ComplexUnmarshaller):
    @property
    def types_unmarshallers(self) -> List["BaseSchemaUnmarshaller"]:
        types = self.schema.getkey("type", ["any"])
        unmarshaller = partial(self.unmarshallers_factory.create, self.schema)
        return list(map(unmarshaller, types))

    @property
    def type(self) -> List[str]:
        types = self.schema.getkey("type", ["any"])
        assert isinstance(types, list)
        return types

    def _get_unmarshallers_iter(self) -> Iterator["BaseSchemaUnmarshaller"]:
        for schema_type in self.type:
            yield self.unmarshallers_factory.create(
                self.schema, type_override=schema_type
            )

    def _get_best_unmarshaller(self, value: Any) -> "BaseSchemaUnmarshaller":
        for unmarshaller in self._get_unmarshallers_iter():
            # validate with validator of formatter (usualy type validator)
            try:
                unmarshaller._validate_format(value)
            except ValidateError:
                continue
            else:
                return unmarshaller

        raise UnmarshallerError("Unmarshaller not found for type(s)")

    def unmarshal(self, value: Any) -> Any:
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

    def unmarshal(self, value: Any) -> Any:
        one_of_schema = self._get_one_of_schema(value)
        if one_of_schema:
            return self.unmarshallers_factory.create(one_of_schema)(value)

        any_of_schema = self._get_any_of_schema(value)
        if any_of_schema:
            return self.unmarshallers_factory.create(any_of_schema)(value)

        all_of_schema = self._get_all_of_schema(value)
        if all_of_schema:
            return self.unmarshallers_factory.create(all_of_schema)(value)

        return super().unmarshal(value)

    def _get_one_of_schema(self, value: Any) -> Optional[Spec]:
        if "oneOf" not in self.schema:
            return None

        one_of_schemas = self.schema / "oneOf"
        for subschema in one_of_schemas:
            unmarshaller = self.unmarshallers_factory.create(subschema)
            try:
                unmarshaller.validate(value)
            except ValidateError:
                continue
            else:
                return subschema
        return None

    def _get_any_of_schema(self, value: Any) -> Optional[Spec]:
        if "anyOf" not in self.schema:
            return None

        any_of_schemas = self.schema / "anyOf"
        for subschema in any_of_schemas:
            unmarshaller = self.unmarshallers_factory.create(subschema)
            try:
                unmarshaller.validate(value)
            except ValidateError:
                continue
            else:
                return subschema
        return None

    def _get_all_of_schema(self, value: Any) -> Optional[Spec]:
        if "allOf" not in self.schema:
            return None

        all_of_schemas = self.schema / "allOf"
        for subschema in all_of_schemas:
            if "type" not in subschema:
                continue
            unmarshaller = self.unmarshallers_factory.create(subschema)
            try:
                unmarshaller.validate(value)
            except ValidateError:
                continue
            else:
                return subschema
        return None
