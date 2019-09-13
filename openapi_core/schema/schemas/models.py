"""OpenAPI core schemas models module"""
import attr
import functools
import logging
from collections import defaultdict
from datetime import date, datetime
from uuid import UUID
import re
import warnings

from six import iteritems, integer_types, binary_type, text_type
from jsonschema.exceptions import ValidationError

from openapi_core.extensions.models.factories import ModelFactory
from openapi_core.schema.schemas._format import oas30_format_checker
from openapi_core.schema.schemas.enums import SchemaFormat, SchemaType
from openapi_core.schema.schemas.exceptions import (
    InvalidSchemaValue, UndefinedSchemaProperty, MissingSchemaProperty,
    OpenAPISchemaError, NoValidSchema,
    UndefinedItemsSchema, InvalidCustomFormatSchemaValue, InvalidSchemaProperty,
    UnmarshallerStrictTypeError,
)
from openapi_core.schema.schemas.util import (
    forcebool, format_date, format_datetime, format_byte, format_uuid,
    format_number,
)
from openapi_core.schema.schemas.validators import OAS30Validator

log = logging.getLogger(__name__)


@attr.s
class Format(object):
    unmarshal = attr.ib()
    validate = attr.ib()


class Schema(object):
    """Represents an OpenAPI Schema."""

    TYPE_CAST_CALLABLE_GETTER = {
        SchemaType.INTEGER: int,
        SchemaType.NUMBER: float,
        SchemaType.BOOLEAN: forcebool,
    }

    DEFAULT_UNMARSHAL_CALLABLE_GETTER = {
    }

    def __init__(
            self, schema_type=None, model=None, properties=None, items=None,
            schema_format=None, required=None, default=None, nullable=False,
            enum=None, deprecated=False, all_of=None, one_of=None,
            additional_properties=True, min_items=None, max_items=None,
            min_length=None, max_length=None, pattern=None, unique_items=False,
            minimum=None, maximum=None, multiple_of=None,
            exclusive_minimum=False, exclusive_maximum=False,
            min_properties=None, max_properties=None, _source=None):
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

        self._source = _source

    @property
    def __dict__(self):
        return self._source or self.to_dict()

    def to_dict(self):
        from openapi_core.schema.schemas.factories import SchemaDictFactory
        return SchemaDictFactory().create(self)

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

    def are_additional_properties_allowed(self, one_of_schema=None):
        return (
            (self.additional_properties is not False) and
            (one_of_schema is None or
                one_of_schema.additional_properties is not False)
        )

    def get_cast_mapping(self):
        mapping = self.TYPE_CAST_CALLABLE_GETTER.copy()
        mapping.update({
            SchemaType.ARRAY: self._cast_collection,
        })

        return defaultdict(lambda: lambda x: x, mapping)

    def cast(self, value):
        """Cast value from string to schema type"""
        if value is None:
            return value

        cast_mapping = self.get_cast_mapping()

        cast_callable = cast_mapping[self.type]
        try:
            return cast_callable(value)
        except ValueError:
            raise InvalidSchemaValue(
                "Failed to cast value {value} to type {type}", value, self.type)

    def _cast_collection(self, value):
        return list(map(self.items.cast, value))

    def get_unmarshal_mapping(self, custom_formatters=None, strict=True):
        primitive_unmarshallers = self.get_primitive_unmarshallers(
            custom_formatters=custom_formatters)

        primitive_unmarshallers_partial = dict(
            (t, functools.partial(u, type_format=self.format, strict=strict))
            for t, u in primitive_unmarshallers.items()
        )

        pass_defaults = lambda f: functools.partial(
          f, custom_formatters=custom_formatters, strict=strict)
        mapping = self.DEFAULT_UNMARSHAL_CALLABLE_GETTER.copy()
        mapping.update(primitive_unmarshallers_partial)
        mapping.update({
            SchemaType.ANY: pass_defaults(self._unmarshal_any),
            SchemaType.ARRAY: pass_defaults(self._unmarshal_collection),
            SchemaType.OBJECT: pass_defaults(self._unmarshal_object),
        })

        return defaultdict(lambda: lambda x: x, mapping)

    def get_validator(self, resolver=None):
        return OAS30Validator(
            self.__dict__, resolver=resolver, format_checker=oas30_format_checker)

    def validate(self, value, resolver=None):
        validator = self.get_validator(resolver=resolver)
        try:
            return validator.validate(value)
        except ValidationError:
            # TODO: pass validation errors
            raise InvalidSchemaValue("Value not valid for schema", value, self.type)

    def unmarshal(self, value, custom_formatters=None, strict=True):
        """Unmarshal parameter from the value."""
        if self.deprecated:
            warnings.warn("The schema is deprecated", DeprecationWarning)
        if value is None:
            if not self.nullable:
                raise InvalidSchemaValue("Null value for non-nullable schema", value, self.type)
            return self.default

        if self.enum and value not in self.enum:
            raise InvalidSchemaValue(
                "Value {value} not in enum choices: {type}", value, self.enum)

        unmarshal_mapping = self.get_unmarshal_mapping(
            custom_formatters=custom_formatters, strict=strict)

        if self.type is not SchemaType.STRING and value == '':
            return None

        unmarshal_callable = unmarshal_mapping[self.type]
        try:
            unmarshalled = unmarshal_callable(value)
        except UnmarshallerStrictTypeError:
            raise InvalidSchemaValue(
                "Value {value} is not of type {type}", value, self.type)
        except ValueError:
            raise InvalidSchemaValue(
                "Failed to unmarshal value {value} to type {type}", value, self.type)

        return unmarshalled

    def get_primitive_unmarshallers(self, **options):
        from openapi_core.schema.schemas.unmarshallers import (
            StringUnmarshaller, BooleanUnmarshaller, IntegerUnmarshaller,
            NumberUnmarshaller,
        )

        unmarshallers_classes = {
            SchemaType.STRING: StringUnmarshaller,
            SchemaType.BOOLEAN: BooleanUnmarshaller,
            SchemaType.INTEGER: IntegerUnmarshaller,
            SchemaType.NUMBER: NumberUnmarshaller,
        }

        unmarshallers = dict(
            (t, klass(**options))
            for t, klass in unmarshallers_classes.items()
        )

        return unmarshallers

    def _unmarshal_any(self, value, custom_formatters=None, strict=True):
        types_resolve_order = [
            SchemaType.OBJECT, SchemaType.ARRAY, SchemaType.BOOLEAN,
            SchemaType.INTEGER, SchemaType.NUMBER, SchemaType.STRING,
        ]
        unmarshal_mapping = self.get_unmarshal_mapping()
        if self.one_of:
            result = None
            for subschema in self.one_of:
                try:
                    unmarshalled = subschema.unmarshal(value, custom_formatters)
                except (OpenAPISchemaError, TypeError, ValueError):
                    continue
                else:
                    if result is not None:
                        log.warning("multiple valid oneOf schemas found")
                        continue
                    result = unmarshalled

            if result is None:
                log.warning("valid oneOf schema not found")

            return result
        else:
            for schema_type in types_resolve_order:
                unmarshal_callable = unmarshal_mapping[schema_type]
                try:
                    return unmarshal_callable(value)
                except UnmarshallerStrictTypeError:
                    continue
                except (OpenAPISchemaError, TypeError):
                    continue

        log.warning("failed to unmarshal any type")
        return value

    def _unmarshal_collection(self, value, custom_formatters=None, strict=True):
        if not isinstance(value, (list, tuple)):
            raise InvalidSchemaValue("Value {value} is not of type {type}", value, self.type)

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
                    unmarshalled = self._unmarshal_properties(
                        value, one_of_schema, custom_formatters=custom_formatters)
                except OpenAPISchemaError:
                    pass
                else:
                    if properties is not None:
                        log.warning("multiple valid oneOf schemas found")
                        continue
                    properties = unmarshalled

            if properties is None:
                log.warning("valid oneOf schema not found")

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

            properties[prop_name] = prop.unmarshal(
                prop_value, custom_formatters=custom_formatters)

        return properties
