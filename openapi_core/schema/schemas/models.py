"""OpenAPI core schemas models module"""
import logging
from collections import defaultdict
import warnings

from six import iteritems

from openapi_core.exceptions import (
    InvalidValueType, UndefinedSchemaProperty, MissingProperty, InvalidValue,
)
from openapi_core.extensions.models.factories import ModelFactory
from openapi_core.schema.schemas.enums import SchemaType, SchemaFormat
from openapi_core.schema.schemas.util import forcebool

log = logging.getLogger(__name__)


class Schema(object):
    """Represents an OpenAPI Schema."""

    DEFAULT_CAST_CALLABLE_GETTER = {
        SchemaType.INTEGER: int,
        SchemaType.NUMBER: float,
        SchemaType.BOOLEAN: forcebool,
    }

    def __init__(
            self, schema_type=None, model=None, properties=None, items=None,
            schema_format=None, required=None, default=None, nullable=False,
            enum=None, deprecated=False, all_of=None):
        self.type = schema_type and SchemaType(schema_type)
        self.model = model
        self.properties = properties and dict(properties) or {}
        self.items = items
        self.format = SchemaFormat(schema_format)
        self.required = required or []
        self.default = default
        self.nullable = nullable
        self.enum = enum
        self.deprecated = deprecated
        self.all_of = all_of and list(all_of) or []

    def __getitem__(self, name):
        return self.properties[name]

    def get_all_properties(self):
        properties = self.properties.copy()

        for subschema in self.all_of:
            subschema_props = subschema.get_all_properties()
            properties.update(subschema_props)

        return properties

    def get_all_required_properties(self):
        required = self.required.copy()

        for subschema in self.all_of:
            subschema_req = subschema.get_all_required_properties()
            required += subschema_req

        return required

    def get_cast_mapping(self):
        mapping = self.DEFAULT_CAST_CALLABLE_GETTER.copy()
        mapping.update({
            SchemaType.ARRAY: self._unmarshal_collection,
            SchemaType.OBJECT: self._unmarshal_object,
        })

        return defaultdict(lambda: lambda x: x, mapping)

    def cast(self, value):
        """Cast value to schema type"""
        if value is None:
            if not self.nullable:
                raise InvalidValueType("Null value for non-nullable schema")
            return self.default

        if self.type is None:
            return value

        cast_mapping = self.get_cast_mapping()

        if self.type in cast_mapping and value == '':
            return None

        cast_callable = cast_mapping[self.type]
        try:
            return cast_callable(value)
        except ValueError:
            raise InvalidValueType(
                "Failed to cast value of {0} to {1}".format(value, self.type)
            )

    def unmarshal(self, value):
        """Unmarshal parameter from the value."""
        if self.deprecated:
            warnings.warn(
                "The schema is deprecated", DeprecationWarning)
        casted = self.cast(value)

        if casted is None and not self.required:
            return None

        if self.enum and casted not in self.enum:
            raise InvalidValue(
                "Value of {0} not in enum choices: {1}".format(
                    value, self.enum)
            )

        return casted

    def _unmarshal_collection(self, value):
        return list(map(self.items.unmarshal, value))

    def _unmarshal_object(self, value):
        if not isinstance(value, (dict, )):
            raise InvalidValueType("Value of {0} not an object".format(value))

        all_properties = self.get_all_properties()
        all_required_properties = self.get_all_required_properties()
        all_properties_keys = all_properties.keys()
        value_keys = value.keys()

        extra_props = set(value_keys) - set(all_properties_keys)

        if extra_props:
            raise UndefinedSchemaProperty(
                "Undefined properties in schema: {0}".format(extra_props))

        properties = {}
        for prop_name, prop in iteritems(all_properties):
            try:
                prop_value = value[prop_name]
            except KeyError:
                if prop_name in all_required_properties:
                    raise MissingProperty(
                        "Missing schema property {0}".format(prop_name))
                if not prop.nullable and not prop.default:
                    continue
                prop_value = prop.default
            properties[prop_name] = prop.unmarshal(prop_value)
        return ModelFactory().create(properties, name=self.model)
