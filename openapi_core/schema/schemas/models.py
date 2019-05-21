"""OpenAPI core schemas models module"""
import attr
import functools
import logging
from base64 import b64decode, b64encode
from collections import defaultdict
from datetime import date, datetime
from uuid import UUID
import re
import warnings

from six import iteritems, integer_types, binary_type, text_type

from openapi_core.extensions.models.factories import ModelFactory
from openapi_core.schema.schemas.enums import SchemaFormat, SchemaType
from openapi_core.schema.schemas.exceptions import (
    InvalidSchemaValue, UndefinedSchemaProperty, MissingSchemaProperty,
    OpenAPISchemaError, NoOneOfSchema, MultipleOneOfSchema, NoValidSchema,
    UndefinedItemsSchema, InvalidCustomFormatSchemaValue, InvalidSchemaProperty,
)
from openapi_core.schema.schemas.util import (
    forcebool, format_date, format_datetime, format_byte, format_uuid,
    format_number,
)
from openapi_core.schema.schemas.validators import (
    TypeValidator, AttributeValidator,
)

log = logging.getLogger(__name__)


@attr.s
class Format(object):
    unmarshal = attr.ib()
    validate = attr.ib()


class Schema(object):
    """Represents an OpenAPI Schema."""

    DEFAULT_CAST_CALLABLE_GETTER = {
    }

    STRING_FORMAT_CALLABLE_GETTER = {
        SchemaFormat.NONE: Format(text_type, TypeValidator(text_type)),
        SchemaFormat.PASSWORD: Format(text_type, TypeValidator(text_type)),
        SchemaFormat.DATE: Format(
            format_date, TypeValidator(date, exclude=datetime)),
        SchemaFormat.DATETIME: Format(format_datetime, TypeValidator(datetime)),
        SchemaFormat.BINARY: Format(binary_type, TypeValidator(binary_type)),
        SchemaFormat.UUID: Format(format_uuid, TypeValidator(UUID)),
        SchemaFormat.BYTE: Format(format_byte, TypeValidator(text_type)),
    }

    NUMBER_FORMAT_CALLABLE_GETTER = {
        SchemaFormat.NONE: Format(format_number, TypeValidator(
            integer_types + (float, ), exclude=bool)),
        SchemaFormat.FLOAT: Format(float, TypeValidator(float)),
        SchemaFormat.DOUBLE: Format(float, TypeValidator(float)),
    }

    TYPE_VALIDATOR_CALLABLE_GETTER = {
        SchemaType.ANY: lambda x: True,
        SchemaType.BOOLEAN: TypeValidator(bool),
        SchemaType.INTEGER: TypeValidator(integer_types, exclude=bool),
        SchemaType.NUMBER: TypeValidator(
            integer_types + (float, ), exclude=bool),
        SchemaType.STRING: TypeValidator(
            text_type, date, datetime, binary_type, UUID),
        SchemaType.ARRAY: TypeValidator(list, tuple),
        SchemaType.OBJECT: AttributeValidator('__dict__'),
    }

    def __init__(
            self, schema_type=None, model=None, properties=None, items=None,
            schema_format=None, required=None, default=None, nullable=False,
            enum=None, deprecated=False, all_of=None, one_of=None,
            additional_properties=True, min_items=None, max_items=None,
            min_length=None, max_length=None, pattern=None, unique_items=False,
            minimum=None, maximum=None, multiple_of=None,
            exclusive_minimum=False, exclusive_maximum=False,
            min_properties=None, max_properties=None):
        self.type = SchemaType(schema_type)
        self.model = model
        self.properties = properties and dict(properties) or {}
        self.items = items
        self.format = schema_format
        self.required = required or []
        self.default = default
        self.nullable = nullable
        self.enum = enum
        self.deprecated = deprecated
        self.all_of = all_of and list(all_of) or []
        self.one_of = one_of and list(one_of) or []
        self.additional_properties = additional_properties
        self.min_items = int(min_items) if min_items is not None else None
        self.max_items = int(max_items) if max_items is not None else None
        self.min_length = int(min_length) if min_length is not None else None
        self.max_length = int(max_length) if max_length is not None else None
        self.pattern = pattern and re.compile(pattern) or None
        self.unique_items = unique_items
        self.minimum = int(minimum) if minimum is not None else None
        self.maximum = int(maximum) if maximum is not None else None
        self.multiple_of = int(multiple_of)\
            if multiple_of is not None else None
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.min_properties = int(min_properties)\
            if min_properties is not None else None
        self.max_properties = int(max_properties)\
            if max_properties is not None else None

        self._all_required_properties_cache = None
        self._all_optional_properties_cache = None

    def __getitem__(self, name):
        return self.properties[name]

    def get_all_properties(self):
        properties = self.properties.copy()

        for subschema in self.all_of:
            subschema_props = subschema.get_all_properties()
            properties.update(subschema_props)

        return properties

    def get_all_properties_names(self):
        all_properties = self.get_all_properties()
        return set(all_properties.keys())

    def get_all_required_properties(self):
        if self._all_required_properties_cache is None:
            self._all_required_properties_cache =\
                self._get_all_required_properties()

        return self._all_required_properties_cache

    def _get_all_required_properties(self):
        all_properties = self.get_all_properties()
        required = self.get_all_required_properties_names()

        return dict(
            (prop_name, val)
            for prop_name, val in iteritems(all_properties)
            if prop_name in required
        )

    def get_all_required_properties_names(self):
        required = self.required[:]

        for subschema in self.all_of:
            subschema_req = subschema.get_all_required_properties()
            required += subschema_req

        return set(required)

    def get_cast_mapping(self, custom_formatters=None, strict=True):
        pass_defaults = lambda f: functools.partial(
          f, custom_formatters=custom_formatters, strict=strict)
        mapping = self.DEFAULT_CAST_CALLABLE_GETTER.copy()
        mapping.update({
            SchemaType.STRING: pass_defaults(self._unmarshal_string),
            SchemaType.BOOLEAN: pass_defaults(self._unmarshal_boolean),
            SchemaType.INTEGER: pass_defaults(self._unmarshal_integer),
            SchemaType.NUMBER: pass_defaults(self._unmarshal_number),
            SchemaType.ANY: pass_defaults(self._unmarshal_any),
            SchemaType.ARRAY: pass_defaults(self._unmarshal_collection),
            SchemaType.OBJECT: pass_defaults(self._unmarshal_object),
        })

        return defaultdict(lambda: lambda x: x, mapping)

    def are_additional_properties_allowed(self, one_of_schema=None):
        return (
            (self.additional_properties is not False) and
            (one_of_schema is None or
                one_of_schema.additional_properties is not False)
        )

    def cast(self, value, custom_formatters=None, strict=True):
        """Cast value to schema type"""
        if value is None:
            if not self.nullable:
                raise InvalidSchemaValue("Null value for non-nullable schema", value, self.type)
            return self.default

        cast_mapping = self.get_cast_mapping(
            custom_formatters=custom_formatters, strict=strict)

        if self.type is not SchemaType.STRING and value == '':
            return None

        cast_callable = cast_mapping[self.type]
        try:
            return cast_callable(value)
        except ValueError:
            raise InvalidSchemaValue(
                "Failed to cast value {value} to type {type}", value, self.type)

    def unmarshal(self, value, custom_formatters=None, strict=True):
        """Unmarshal parameter from the value."""
        if self.deprecated:
            warnings.warn("The schema is deprecated", DeprecationWarning)

        casted = self.cast(value, custom_formatters=custom_formatters, strict=strict)

        if casted is None and not self.required:
            return None

        if self.enum and casted not in self.enum:
            raise InvalidSchemaValue(
                "Value {value} not in enum choices: {type}", value, self.enum)

        return casted

    def _unmarshal_string(self, value, custom_formatters=None, strict=True):
        if strict and not isinstance(value, (text_type, binary_type)):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

        try:
            schema_format = SchemaFormat(self.format)
        except ValueError:
            msg = "Unsupported format {type} unmarshalling for value {value}"
            if custom_formatters is not None:
                formatstring = custom_formatters.get(self.format)
                if formatstring is None:
                    raise InvalidSchemaValue(msg, value, self.format)
            else:
                raise InvalidSchemaValue(msg, value, self.format)
        else:
            formatstring = self.STRING_FORMAT_CALLABLE_GETTER[schema_format]

        try:
            return formatstring.unmarshal(value)
        except ValueError as exc:
            raise InvalidCustomFormatSchemaValue(
                "Failed to format value {value} to format {type}: {exception}", value, self.format, exc)

    def _unmarshal_integer(self, value, custom_formatters=None, strict=True):
        if strict and not isinstance(value, integer_types):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

        return int(value)

    def _unmarshal_number(self, value, custom_formatters=None, strict=True):
        if strict and not isinstance(value, (float, ) + integer_types):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

        try:
            schema_format = SchemaFormat(self.format)
        except ValueError:
            msg = "Unsupported format {type} unmarshalling for value {value}"
            if custom_formatters is not None:
                formatnumber = custom_formatters.get(self.format)
                if formatnumber is None:
                    raise InvalidSchemaValue(msg, value, self.format)
            else:
                raise InvalidSchemaValue(msg, value, self.format)
        else:
            formatnumber = self.NUMBER_FORMAT_CALLABLE_GETTER[schema_format]

        try:
            return formatnumber.unmarshal(value)
        except ValueError as exc:
            raise InvalidCustomFormatSchemaValue(
                "Failed to format value {value} to format {type}: {exception}", value, self.format, exc)

    def _unmarshal_boolean(self, value, custom_formatters=None, strict=True):
        if strict and not isinstance(value, (bool, )):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

        return forcebool(value)

    def _unmarshal_any(self, value, custom_formatters=None, strict=True):
        types_resolve_order = [
            SchemaType.OBJECT, SchemaType.ARRAY, SchemaType.BOOLEAN,
            SchemaType.INTEGER, SchemaType.NUMBER, SchemaType.STRING,
        ]
        cast_mapping = self.get_cast_mapping()
        for schema_type in types_resolve_order:
            cast_callable = cast_mapping[schema_type]
            try:
                return cast_callable(value)
            # @todo: remove ValueError when validation separated
            except (OpenAPISchemaError, TypeError, ValueError):
                continue

        raise NoValidSchema(value)

    def _unmarshal_collection(self, value, custom_formatters=None, strict=True):
        if not isinstance(value, (list, tuple)):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

        if self.items is None:
            raise UndefinedItemsSchema(self.type)

        f = functools.partial(
            self.items.unmarshal,
            custom_formatters=custom_formatters, strict=strict,
        )
        return list(map(f, value))

    def _unmarshal_object(self, value, model_factory=None,
                          custom_formatters=None, strict=True):
        if not isinstance(value, (dict, )):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

        model_factory = model_factory or ModelFactory()

        if self.one_of:
            properties = None
            for one_of_schema in self.one_of:
                try:
                    found_props = self._unmarshal_properties(
                        value, one_of_schema, custom_formatters=custom_formatters)
                except OpenAPISchemaError:
                    pass
                else:
                    if properties is not None:
                        raise MultipleOneOfSchema(self.type)
                    properties = found_props

            if properties is None:
                raise NoOneOfSchema(self.type)

        else:
            properties = self._unmarshal_properties(
              value, custom_formatters=custom_formatters)

        return model_factory.create(properties, name=self.model)

    def _unmarshal_properties(self, value, one_of_schema=None,
                              custom_formatters=None, strict=True):
        all_props = self.get_all_properties()
        all_props_names = self.get_all_properties_names()
        all_req_props_names = self.get_all_required_properties_names()

        if one_of_schema is not None:
            all_props.update(one_of_schema.get_all_properties())
            all_props_names |= one_of_schema.\
                get_all_properties_names()
            all_req_props_names |= one_of_schema.\
                get_all_required_properties_names()

        value_props_names = value.keys()
        extra_props = set(value_props_names) - set(all_props_names)
        extra_props_allowed = self.are_additional_properties_allowed(
            one_of_schema)
        if extra_props and not extra_props_allowed:
            raise UndefinedSchemaProperty(extra_props)

        properties = {}
        if self.additional_properties is not True:
            for prop_name in extra_props:
                prop_value = value[prop_name]
                properties[prop_name] = self.additional_properties.unmarshal(
                    prop_value, custom_formatters=custom_formatters)

        for prop_name, prop in iteritems(all_props):
            try:
                prop_value = value[prop_name]
            except KeyError:
                if prop_name in all_req_props_names:
                    raise MissingSchemaProperty(prop_name)
                if not prop.nullable and not prop.default:
                    continue
                prop_value = prop.default
            try:
                properties[prop_name] = prop.unmarshal(
                  prop_value, custom_formatters=custom_formatters)
            except OpenAPISchemaError as exc:
                raise InvalidSchemaProperty(prop_name, exc)

        self._validate_properties(properties, one_of_schema=one_of_schema,
                                  custom_formatters=custom_formatters)

        return properties

    def get_validator_mapping(self):
        mapping = {
            SchemaType.ARRAY: self._validate_collection,
            SchemaType.STRING: self._validate_string,
            SchemaType.OBJECT: self._validate_object,
            SchemaType.INTEGER: self._validate_number,
            SchemaType.NUMBER: self._validate_number,
        }

        def default(x, **kw):
            return x

        return defaultdict(lambda: default, mapping)

    def validate(self, value, custom_formatters=None):
        if value is None:
            if not self.nullable:
                raise InvalidSchemaValue("Null value for non-nullable schema of type {type}", value, self.type)
            return

        # type validation
        type_validator_callable = self.TYPE_VALIDATOR_CALLABLE_GETTER[
            self.type]
        if not type_validator_callable(value):
            raise InvalidSchemaValue(
                "Value {value} not valid type {type}", value, self.type.value)

        # structure validation
        validator_mapping = self.get_validator_mapping()
        validator_callable = validator_mapping[self.type]
        validator_callable(value, custom_formatters=custom_formatters)

        return value

    def _validate_collection(self, value, custom_formatters=None):
        if self.items is None:
            raise UndefinedItemsSchema(self.type)

        if self.min_items is not None:
            if self.min_items < 0:
                raise OpenAPISchemaError(
                    "Schema for collection invalid:"
                    " minItems must be non-negative"
                )
            if len(value) < self.min_items:
                raise InvalidSchemaValue(
                    "Value must contain at least {type} item(s),"
                    " {value} found", len(value), self.min_items)
        if self.max_items is not None:
            if self.max_items < 0:
                raise OpenAPISchemaError(
                    "Schema for collection invalid:"
                    " maxItems must be non-negative"
                )
            if len(value) > self.max_items:
                raise InvalidSchemaValue(
                    "Value must contain at most {value} item(s),"
                    " {type} found", len(value), self.max_items)
        if self.unique_items and len(set(value)) != len(value):
            raise OpenAPISchemaError("Value may not contain duplicate items")

        f = functools.partial(self.items.validate,
                              custom_formatters=custom_formatters)
        return list(map(f, value))

    def _validate_number(self, value, custom_formatters=None):
        if self.minimum is not None:
            if self.exclusive_minimum and value <= self.minimum:
                raise InvalidSchemaValue(
                    "Value {value} is not less than or equal to {type}", value, self.minimum)
            elif value < self.minimum:
                raise InvalidSchemaValue(
                    "Value {value} is not less than {type}", value, self.minimum)

        if self.maximum is not None:
            if self.exclusive_maximum and value >= self.maximum:
                raise InvalidSchemaValue(
                    "Value {value} is not greater than or equal to {type}", value, self.maximum)
            elif value > self.maximum:
                raise InvalidSchemaValue(
                    "Value {value} is not greater than {type}", value, self.maximum)

        if self.multiple_of is not None and value % self.multiple_of:
            raise InvalidSchemaValue(
                "Value {value} is not a multiple of {type}",
                    value, self.multiple_of)

    def _validate_string(self, value, custom_formatters=None):
        try:
            schema_format = SchemaFormat(self.format)
        except ValueError:
            msg = "Unsupported {0} format validation".format(self.format)
            if custom_formatters is not None:
                formatstring = custom_formatters.get(self.format)
                if formatstring is None:
                    raise OpenAPISchemaError(msg)
            else:
                raise OpenAPISchemaError(msg)
        else:
            formatstring =\
                self.STRING_FORMAT_CALLABLE_GETTER[schema_format]

        if not formatstring.validate(value):
            raise InvalidSchemaValue(
                "Value {value} not valid format {type}", value, self.format)

        if self.min_length is not None:
            if self.min_length < 0:
                raise OpenAPISchemaError(
                    "Schema for string invalid:"
                    " minLength must be non-negative"
                )
            if len(value) < self.min_length:
                raise InvalidSchemaValue(
                    "Value is shorter ({value}) than the minimum length of {type}",
                    len(value), self.min_length
                )
        if self.max_length is not None:
            if self.max_length < 0:
                raise OpenAPISchemaError(
                    "Schema for string invalid:"
                    " maxLength must be non-negative"
                )
            if len(value) > self.max_length:
                raise InvalidSchemaValue(
                    "Value is longer ({value}) than the maximum length of {type}",
                    len(value), self.max_length
                )
        if self.pattern is not None and not self.pattern.search(value):
            raise InvalidSchemaValue(
                "Value {value} does not match the pattern {type}",
                    value, self.pattern.pattern
            )

        return True

    def _validate_object(self, value, custom_formatters=None):
        properties = value.__dict__

        if self.one_of:
            valid_one_of_schema = None
            for one_of_schema in self.one_of:
                try:
                    self._validate_properties(
                      properties, one_of_schema,
                      custom_formatters=custom_formatters)
                except OpenAPISchemaError:
                    pass
                else:
                    if valid_one_of_schema is not None:
                        raise MultipleOneOfSchema(self.type)
                    valid_one_of_schema = True

            if valid_one_of_schema is None:
                raise NoOneOfSchema(self.type)

        else:
            self._validate_properties(properties,
                                      custom_formatters=custom_formatters)

        if self.min_properties is not None:
            if self.min_properties < 0:
                raise OpenAPISchemaError(
                    "Schema for object invalid:"
                    " minProperties must be non-negative"
                )

            if len(properties) < self.min_properties:
                raise InvalidSchemaValue(
                    "Value must contain at least {type} properties,"
                    " {value} found", len(properties), self.min_properties
                )

        if self.max_properties is not None:
            if self.max_properties < 0:
                raise OpenAPISchemaError(
                    "Schema for object invalid:"
                    " maxProperties must be non-negative"
                )
            if len(properties) > self.max_properties:
                raise InvalidSchemaValue(
                    "Value must contain at most {type} properties,"
                    " {value} found", len(properties), self.max_properties
                )

        return True

    def _validate_properties(self, value, one_of_schema=None,
                             custom_formatters=None):
        all_props = self.get_all_properties()
        all_props_names = self.get_all_properties_names()
        all_req_props_names = self.get_all_required_properties_names()

        if one_of_schema is not None:
            all_props.update(one_of_schema.get_all_properties())
            all_props_names |= one_of_schema.\
                get_all_properties_names()
            all_req_props_names |= one_of_schema.\
                get_all_required_properties_names()

        value_props_names = value.keys()
        extra_props = set(value_props_names) - set(all_props_names)
        extra_props_allowed = self.are_additional_properties_allowed(
            one_of_schema)
        if extra_props and not extra_props_allowed:
            raise UndefinedSchemaProperty(extra_props)

        if self.additional_properties is not True:
            for prop_name in extra_props:
                prop_value = value[prop_name]
                self.additional_properties.validate(
                    prop_value, custom_formatters=custom_formatters)

        for prop_name, prop in iteritems(all_props):
            try:
                prop_value = value[prop_name]
            except KeyError:
                if prop_name in all_req_props_names:
                    raise MissingSchemaProperty(prop_name)
                if not prop.nullable and not prop.default:
                    continue
                prop_value = prop.default
            try:
                prop.validate(prop_value, custom_formatters=custom_formatters)
            except OpenAPISchemaError as exc:
                raise InvalidSchemaProperty(prop_name, original_exception=exc)

        return True
