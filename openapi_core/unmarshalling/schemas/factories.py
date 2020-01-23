import warnings

from openapi_core.schema.schemas.enums import SchemaType, SchemaFormat
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.unmarshallers import (
    StringUnmarshaller, IntegerUnmarshaller, NumberUnmarshaller,
    BooleanUnmarshaller, ArrayUnmarshaller, ObjectUnmarshaller,
    AnyUnmarshaller,
)


class SchemaUnmarshallersFactory(object):

    PRIMITIVE_UNMARSHALLERS = {
        SchemaType.STRING: StringUnmarshaller,
        SchemaType.INTEGER: IntegerUnmarshaller,
        SchemaType.NUMBER: NumberUnmarshaller,
        SchemaType.BOOLEAN: BooleanUnmarshaller,
    }
    COMPLEX_UNMARSHALLERS = {
        SchemaType.ARRAY: ArrayUnmarshaller,
        SchemaType.OBJECT: ObjectUnmarshaller,
        SchemaType.ANY: AnyUnmarshaller,
    }

    def __init__(self, custom_formatters=None):
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters

    def create(self, schema, type_override=None):
        """Create unmarshaller from the schema."""
        if schema.deprecated:
            warnings.warn("The schema is deprecated", DeprecationWarning)

        schema_type = type_override or schema.type
        if schema_type in self.PRIMITIVE_UNMARSHALLERS:
            klass = self.PRIMITIVE_UNMARSHALLERS[schema_type]
            kwargs = dict(schema=schema)

        elif schema_type in self.COMPLEX_UNMARSHALLERS:
            klass = self.COMPLEX_UNMARSHALLERS[schema_type]
            kwargs = dict(schema=schema, unmarshallers_factory=self)

        formatter = self.get_formatter(klass.FORMATTERS, schema.format)

        if formatter is None:
            raise FormatterNotFoundError(schema.format)

        return klass(formatter, **kwargs)

    def get_formatter(self, formatters, type_format=SchemaFormat.NONE):
        try:
            schema_format = SchemaFormat(type_format)
        except ValueError:
            return self.custom_formatters.get(type_format)
        else:
            if schema_format == SchemaFormat.NONE:
                return lambda x: x
            return formatters.get(schema_format)
