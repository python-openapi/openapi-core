import logging

from six import text_type, binary_type, integer_types
from six import iteritems

from openapi_core.extensions.models.factories import ModelFactory
from openapi_core.schema.schemas.enums import SchemaFormat, SchemaType
from openapi_core.schema.schemas.exceptions import (
    ValidateError,
)
from openapi_core.schema.schemas.types import NoValue
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError,
    InvalidCustomFormatSchemaValue,
    UnmarshallerStrictTypeError,
)
from openapi_core.unmarshalling.schemas.util import (
    forcebool, format_date, format_datetime, format_byte, format_uuid,
    format_number,
)

log = logging.getLogger(__name__)


class StrictUnmarshaller(object):

    STRICT_TYPES = ()

    def __call__(self, value, strict=True):
        if strict and not self._is_strict(value):
            raise UnmarshallerStrictTypeError(value, self.STRICT_TYPES)

        return value

    def _is_strict(self, value):
        if not self.STRICT_TYPES:
            return True

        return isinstance(value, self.STRICT_TYPES)


class PrimitiveTypeUnmarshaller(StrictUnmarshaller):

    FORMATTERS = {}

    def __init__(self, formatter, schema):
        self.formatter = formatter
        self.schema = schema

    def __call__(self, value=NoValue, strict=True):
        if value is NoValue:
            value = self.schema.default
        if value is None:
            return
        value = super(PrimitiveTypeUnmarshaller, self).__call__(
            value, strict=strict)

        return self.format(value)

    def format(self, value):
        try:
            return self.formatter(value)
        except ValueError as exc:
            raise InvalidCustomFormatSchemaValue(
                value, self.schema.format, exc)


class StringUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = (text_type, binary_type)
    FORMATTERS = {
        SchemaFormat.NONE: text_type,
        SchemaFormat.PASSWORD: text_type,
        SchemaFormat.DATE: format_date,
        SchemaFormat.DATETIME: format_datetime,
        SchemaFormat.BINARY: binary_type,
        SchemaFormat.UUID: format_uuid,
        SchemaFormat.BYTE: format_byte,
    }


class IntegerUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = integer_types
    FORMATTERS = {
        SchemaFormat.NONE: int,
        SchemaFormat.INT32: int,
        SchemaFormat.INT64: int,
    }


class NumberUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = (float, ) + integer_types
    FORMATTERS = {
        SchemaFormat.NONE: format_number,
        SchemaFormat.FLOAT: float,
        SchemaFormat.DOUBLE: float,
    }


class BooleanUnmarshaller(PrimitiveTypeUnmarshaller):

    STRICT_TYPES = (bool, )
    FORMATTERS = {
        SchemaFormat.NONE: forcebool,
    }


class ComplexUnmarshaller(PrimitiveTypeUnmarshaller):

    def __init__(self, formatter, schema, unmarshallers_factory):
        super(ComplexUnmarshaller, self).__init__(formatter, schema)
        self.unmarshallers_factory = unmarshallers_factory


class ArrayUnmarshaller(ComplexUnmarshaller):

    STRICT_TYPES = (list, tuple)
    FORMATTERS = {}

    @property
    def items_unmarshaller(self):
        return self.unmarshallers_factory.create(self.schema.items)

    def __call__(self, value=NoValue, strict=True):
        value = super(ArrayUnmarshaller, self).__call__(value, strict=strict)

        self.unmarshallers_factory.create(self.schema.items)

        return list(map(self.items_unmarshaller, value))


class ObjectUnmarshaller(ComplexUnmarshaller):

    STRICT_TYPES = (dict, )
    FORMATTERS = {}

    @property
    def model_factory(self):
        return ModelFactory()

    def __call__(self, value=NoValue, strict=True):
        value = super(ObjectUnmarshaller, self).__call__(value, strict=strict)

        if self.schema.one_of:
            properties = None
            for one_of_schema in self.schema.one_of:
                try:
                    unmarshalled = self._unmarshal_properties(
                        value, one_of_schema, strict=strict)
                except (UnmarshalError, ValueError):
                    pass
                else:
                    if properties is not None:
                        log.warning("multiple valid oneOf schemas found")
                        continue
                    properties = unmarshalled

            if properties is None:
                log.warning("valid oneOf schema not found")

        else:
            properties = self._unmarshal_properties(value)

        if 'x-model' in self.schema.extensions:
            extension = self.schema.extensions['x-model']
            return self.model_factory.create(properties, name=extension.value)

        return properties

    def _unmarshal_properties(
            self, value=NoValue, one_of_schema=None, strict=True):
        all_props = self.schema.get_all_properties()
        all_props_names = self.schema.get_all_properties_names()

        if one_of_schema is not None:
            all_props.update(one_of_schema.get_all_properties())
            all_props_names |= one_of_schema.\
                get_all_properties_names()

        value_props_names = value.keys()
        extra_props = set(value_props_names) - set(all_props_names)

        properties = {}
        if self.schema.additional_properties is not True:
            for prop_name in extra_props:
                prop_value = value[prop_name]
                properties[prop_name] = self.unmarshallers_factory.create(
                    self.schema.additional_properties)(
                        prop_value, strict=strict)

        for prop_name, prop in iteritems(all_props):
            try:
                prop_value = value[prop_name]
            except KeyError:
                if prop.default is NoValue:
                    continue
                prop_value = prop.default

            properties[prop_name] = self.unmarshallers_factory.create(
                prop)(prop_value, strict=strict)

        return properties


class AnyUnmarshaller(ComplexUnmarshaller):

    SCHEMA_TYPES_ORDER = [
        SchemaType.OBJECT, SchemaType.ARRAY, SchemaType.BOOLEAN,
        SchemaType.INTEGER, SchemaType.NUMBER, SchemaType.STRING,
    ]

    def __call__(self, value=NoValue, strict=True):
        one_of_schema = self._get_one_of_schema(value)
        if one_of_schema:
            return self.unmarshallers_factory.create(one_of_schema)(
                value, strict=strict)

        for schema_type in self.SCHEMA_TYPES_ORDER:
            try:
                unmarshaller = self.unmarshallers_factory.create(
                    self.schema, type_override=schema_type)
                return unmarshaller(value, strict=strict)
            except (UnmarshalError, ValueError):
                continue

        log.warning("failed to unmarshal any type")
        return value

    def _get_one_of_schema(self, value):
        if not self.schema.one_of:
            return
        for subschema in self.schema.one_of:
            try:
                subschema.validate(value)
            except ValidateError:
                continue
            else:
                return subschema
