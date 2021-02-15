from functools import partial
import logging

from isodate.isodatetime import parse_datetime

from openapi_schema_validator._types import (
    is_array, is_bool, is_integer,
    is_object, is_number, is_string,
)
from openapi_schema_validator._format import oas30_format_checker
from six import text_type, binary_type
from six import iteritems

from openapi_core.extensions.models.factories import ModelFactory
from openapi_core.schema.schemas.enums import SchemaFormat, SchemaType
from openapi_core.schema.schemas.models import Schema
from openapi_core.schema.schemas.types import NoValue
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError, InvalidSchemaValue,
    InvalidSchemaFormatValue,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.util import (
    forcebool, format_date, format_byte, format_uuid,
    format_number,
)

log = logging.getLogger(__name__)


class PrimitiveTypeUnmarshaller(object):

    FORMATTERS = {}

    def __init__(self, formatter, validator, schema):
        self.formatter = formatter
        self.validator = validator
        self.schema = schema

    def __call__(self, value=NoValue):
        if value is NoValue:
            value = self.schema.default
        if value is None:
            return

        self.validate(value)

        return self.unmarshal(value)

    def _formatter_validate(self, value):
        result = self.formatter.validate(value)
        if not result:
            raise InvalidSchemaValue(value, self.schema.type)

    def validate(self, value):
        errors_iter = self.validator.iter_errors(value)
        errors = tuple(errors_iter)
        if errors:
            raise InvalidSchemaValue(
                value, self.schema.type, schema_errors=errors)

    def unmarshal(self, value):
        try:
            return self.formatter.unmarshal(value)
        except ValueError as exc:
            raise InvalidSchemaFormatValue(
                value, self.schema.format, exc)


class StringUnmarshaller(PrimitiveTypeUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter.from_callables(
            partial(is_string, None), text_type),
        SchemaFormat.PASSWORD: Formatter.from_callables(
            partial(oas30_format_checker.check, format='password'), text_type),
        SchemaFormat.DATE: Formatter.from_callables(
            partial(oas30_format_checker.check, format='date'), format_date),
        SchemaFormat.DATETIME: Formatter.from_callables(
            partial(oas30_format_checker.check, format='date-time'),
            parse_datetime),
        SchemaFormat.BINARY: Formatter.from_callables(
            partial(oas30_format_checker.check, format='binary'), binary_type),
        SchemaFormat.UUID: Formatter.from_callables(
            partial(oas30_format_checker.check, format='uuid'), format_uuid),
        SchemaFormat.BYTE: Formatter.from_callables(
            partial(oas30_format_checker.check, format='byte'), format_byte),
    }


class IntegerUnmarshaller(PrimitiveTypeUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter.from_callables(
            partial(is_integer, None), int),
        SchemaFormat.INT32: Formatter.from_callables(
            partial(oas30_format_checker.check, format='int32'), int),
        SchemaFormat.INT64: Formatter.from_callables(
            partial(oas30_format_checker.check, format='int64'), int),
    }


class NumberUnmarshaller(PrimitiveTypeUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter.from_callables(
            partial(is_number, None), format_number),
        SchemaFormat.FLOAT: Formatter.from_callables(
            partial(oas30_format_checker.check, format='float'), float),
        SchemaFormat.DOUBLE: Formatter.from_callables(
            partial(oas30_format_checker.check, format='double'), float),
    }


class BooleanUnmarshaller(PrimitiveTypeUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter.from_callables(
            partial(is_bool, None), forcebool),
    }


class ComplexUnmarshaller(PrimitiveTypeUnmarshaller):

    def __init__(
            self, formatter, validator, schema, unmarshallers_factory,
            context=None):
        super(ComplexUnmarshaller, self).__init__(formatter, validator, schema)
        self.unmarshallers_factory = unmarshallers_factory
        self.context = context


class ArrayUnmarshaller(ComplexUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter.from_callables(
            partial(is_array, None), list),
    }

    @property
    def items_unmarshaller(self):
        return self.unmarshallers_factory.create(self.schema.items)

    def __call__(self, value=NoValue):
        value = super(ArrayUnmarshaller, self).__call__(value)
        if value is None and self.schema.nullable:
            return None
        return list(map(self.items_unmarshaller, value))


class ObjectUnmarshaller(ComplexUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter.from_callables(
            partial(is_object, None), dict),
    }

    @property
    def model_factory(self):
        return ModelFactory()

    def unmarshal(self, value):
        try:
            value = self.formatter.unmarshal(value)
        except ValueError as exc:
            raise InvalidSchemaFormatValue(
                value, self.schema.format, exc)
        else:
            return self._unmarshal_object(value)

    def _unmarshal_object(self, value=NoValue):
        if self.schema.one_of:
            properties = None
            for one_of_schema in self.schema.one_of:
                try:
                    unmarshalled = self._unmarshal_properties(
                        value, one_of_schema)
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

    def _unmarshal_properties(self, value=NoValue, one_of_schema=None):
        all_props = self.schema.get_all_properties()
        all_props_names = self.schema.get_all_properties_names()

        if one_of_schema is not None:
            all_props.update(one_of_schema.get_all_properties())
            all_props_names |= one_of_schema.\
                get_all_properties_names()

        value_props_names = value.keys()
        extra_props = set(value_props_names) - set(all_props_names)

        properties = {}
        if isinstance(self.schema.additional_properties, Schema):
            for prop_name in extra_props:
                prop_value = value[prop_name]
                properties[prop_name] = self.unmarshallers_factory.create(
                    self.schema.additional_properties)(prop_value)
        elif self.schema.additional_properties is True:
            for prop_name in extra_props:
                prop_value = value[prop_name]
                properties[prop_name] = prop_value

        for prop_name, prop in iteritems(all_props):
            if self.context == UnmarshalContext.REQUEST and prop.read_only:
                continue
            if self.context == UnmarshalContext.RESPONSE and prop.write_only:
                continue
            try:
                prop_value = value[prop_name]
            except KeyError:
                if prop.default is NoValue:
                    continue
                prop_value = prop.default

            properties[prop_name] = self.unmarshallers_factory.create(
                prop)(prop_value)

        return properties


class AnyUnmarshaller(ComplexUnmarshaller):

    FORMATTERS = {
        SchemaFormat.NONE: Formatter(),
    }

    SCHEMA_TYPES_ORDER = [
        SchemaType.OBJECT, SchemaType.ARRAY, SchemaType.BOOLEAN,
        SchemaType.INTEGER, SchemaType.NUMBER, SchemaType.STRING,
    ]

    def unmarshal(self, value=NoValue):
        one_of_schema = self._get_one_of_schema(value)
        if one_of_schema:
            return self.unmarshallers_factory.create(one_of_schema)(value)

        all_of_schema = self._get_all_of_schema(value)
        if all_of_schema:
            return self.unmarshallers_factory.create(all_of_schema)(value)

        for schema_type in self.SCHEMA_TYPES_ORDER:
            unmarshaller = self.unmarshallers_factory.create(
                self.schema, type_override=schema_type)
            # validate with validator of formatter (usualy type validator)
            try:
                unmarshaller._formatter_validate(value)
            except ValidateError:
                continue
            else:
                return unmarshaller(value)

        log.warning("failed to unmarshal any type")
        return value

    def _get_one_of_schema(self, value):
        if not self.schema.one_of:
            return
        for subschema in self.schema.one_of:
            unmarshaller = self.unmarshallers_factory.create(subschema)
            try:
                unmarshaller.validate(value)
            except ValidateError:
                continue
            else:
                return subschema

    def _get_all_of_schema(self, value):
        if not self.schema.all_of:
            return
        for subschema in self.schema.all_of:
            if subschema.type == SchemaType.ANY:
                continue
            unmarshaller = self.unmarshallers_factory.create(subschema)
            try:
                unmarshaller.validate(value)
            except ValidateError:
                continue
            else:
                return subschema
