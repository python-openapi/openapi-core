import logging
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
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
from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.datatypes import FormattersDict
from openapi_core.unmarshalling.schemas.datatypes import SchemaUnmarshaller
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
from openapi_core.unmarshalling.schemas.finders import AllOfSchemasFinder
from openapi_core.unmarshalling.schemas.finders import AnyOfSchemasFinder
from openapi_core.unmarshalling.schemas.finders import OneOfSchemaFinder
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

    TYPE = NotImplemented
    FORMATTERS: FormattersDict = {
        None: Formatter(),
    }

    def __init__(
        self,
        schema: Spec,
        validator: Validator,
        unmarshallers_factory: "SchemaUnmarshallersFactory",
        formatter: Optional[Formatter] = None,
    ):
        self.schema = schema
        self.validator = validator
        self.unmarshallers_factory = unmarshallers_factory

        self.schema_format = schema.getkey("format")
        self.formatter = formatter

    def __call__(self, value: Any) -> Any:
        if value is None:
            return

        self.validate(value)

        return self.unmarshal(value)

    def _clone(self, schema: Spec) -> "ObjectUnmarshaller":
        return self.unmarshallers_factory.create(
            schema,
            type_override=self.TYPE,
        )

    def _find_one_of_schema(self, value: Any) -> Optional[SchemaUnmarshaller]:
        finder = OneOfSchemaFinder(self.schema, self.unmarshallers_factory)
        return finder.find(value)

    def _find_any_of_schemas(self, value: Any) -> Iterable[SchemaUnmarshaller]:
        finder = AnyOfSchemasFinder(self.schema, self.unmarshallers_factory)
        yield from finder.find(value)

    def _find_all_of_schemas(self, value: Any) -> Iterable[SchemaUnmarshaller]:
        finder = AllOfSchemasFinder(self.schema, self.unmarshallers_factory)
        yield from finder.find(value)

    def _get_formatter(self) -> Formatter:
        if self.formatter is not None:
            return self.formatter

        if self.schema_format not in self.FORMATTERS:
            raise FormatterNotFoundError(self.schema_format)
        return self.FORMATTERS[self.schema_format]

    def _get_best_formatter(self, value: Any) -> Formatter:
        if self.formatter is not None:
            return self.formatter

        if self.schema_format is None:
            for schema, unmarshaller in self._find_all_of_schemas(value):
                if "format" in schema:
                    return unmarshaller._get_formatter()

            one_of = self._find_one_of_schema(value)
            if one_of is not None:
                if "format" in one_of.schema:
                    return one_of.unmarshaller._get_formatter()

            for schema, unmarshaller in self._find_any_of_schemas(value):
                if "format" in schema:
                    return unmarshaller._get_formatter()

        if self.schema_format not in self.FORMATTERS:
            raise FormatterNotFoundError(self.schema_format)
        return self.FORMATTERS[self.schema_format]

    def _validate_format(self, value: Any) -> None:
        if self.formatter is not None:
            formatter = self.formatter
        else:
            if self.schema_format not in self.FORMATTERS:
                raise FormatterNotFoundError(self.schema_format)
            formatter = self.FORMATTERS[self.schema_format]

        result = formatter.validate(value)
        if not result:
            raise InvalidSchemaValue(value, self.TYPE)

    def format(self, value: Any) -> Any:
        formatter = self._get_best_formatter(value)
        try:
            return formatter.format(value)
        except ValueError as exc:
            raise InvalidSchemaFormatValue(value, self.schema_format, exc)

    def validate(self, value: Any) -> None:
        errors_iter = self.validator.iter_errors(value)
        errors = tuple(errors_iter)
        if errors:
            raise InvalidSchemaValue(value, self.TYPE, schema_errors=errors)

    def unmarshal(self, value: Any) -> Any:
        return self.format(value)


class StringUnmarshaller(BaseSchemaUnmarshaller):

    TYPE = "string"
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

    TYPE = "integer"
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

    TYPE = "number"
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

    TYPE = "boolean"
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
        unmarshallers_factory: "SchemaUnmarshallersFactory",
        formatter: Optional[Formatter] = None,
        context: Optional[UnmarshalContext] = None,
    ):
        super().__init__(schema, validator, unmarshallers_factory, formatter)
        self.context = context


class ArrayUnmarshaller(ComplexUnmarshaller):

    TYPE = "array"
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
        if value is None and self.schema.getkey("nullable", False):
            return None
        return list(map(self.items_unmarshaller, value))


class ObjectUnmarshaller(ComplexUnmarshaller):

    TYPE = "object"
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

        for _, unmarshaller in self._find_all_of_schemas(value):
            all_of_properties = unmarshaller.format(value)
            properties.update(all_of_properties)

        one_of = self._find_one_of_schema(value)
        if one_of is not None:
            one_of_properties = one_of.unmarshaller.format(value)
            properties.update(one_of_properties)

        for _, unmarshaller in self._find_any_of_schemas(value):
            any_of_properties = unmarshaller.format(value)
            properties.update(any_of_properties)

        schema_properties = self.schema.get("properties", {})
        schema_properties_dict = dict(list(schema_properties.items()))
        for prop_name, prop in schema_properties_dict.items():
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

    def unmarshal(self, value: Any) -> Any:
        for unmarshaller in self.types_unmarshallers:
            # validate with validator of formatter (usualy type validator)
            try:
                unmarshaller._formatter_validate(value)
            except ValidateError:
                continue
            else:
                return unmarshaller(value)

        log.warning("failed to unmarshal multi type")
        return value


class AnyUnmarshaller(ComplexUnmarshaller):

    TYPE = "any"
    SCHEMA_TYPES_ORDER = [
        "object",
        "array",
        "boolean",
        "integer",
        "number",
        "string",
    ]

    _best_unmarshaller: Optional[BaseSchemaUnmarshaller] = None

    def _get_best_unmarshaller(self, value: Any) -> BaseSchemaUnmarshaller:
        for schema_type in self.SCHEMA_TYPES_ORDER:
            unmarshaller = self.unmarshallers_factory.create(
                self.schema, type_override=schema_type
            )
            # validate with validator of formatter (usualy type validator)
            try:
                unmarshaller._validate_format(value)
            except ValidateError:
                continue
            else:
                return unmarshaller

        raise UnmarshallerError("Unmarshaller not found for any type")

    def get_best_unmarshaller(self, value: Any) -> Any:
        if self._best_unmarshaller is None:
            self._best_unmarshaller = self._get_best_unmarshaller(value)
        return self._best_unmarshaller

    def format(self, value: Any) -> Any:
        unmarshaller = self.get_best_unmarshaller(value)
        return unmarshaller.format(value)

    def unmarshal(self, value: Any) -> Any:
        # one_of_schema = self._get_one_of_schema(value)
        # if one_of_schema:
        #     return self.unmarshallers_factory.create(one_of_schema)(value)

        # any_of_schema = self._get_any_of_schema(value)
        # if any_of_schema:
        #     return self.unmarshallers_factory.create(any_of_schema)(value)

        # all_of_schema = self._get_all_of_schema(value)
        # if all_of_schema:
        #     return self.unmarshallers_factory.create(all_of_schema)(value)

        unmarshaller = self.get_best_unmarshaller(value)
        return unmarshaller.unmarshal(value)
