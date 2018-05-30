"""OpenAPI core schemas models module"""
import logging
from collections import defaultdict
import warnings

from six import iteritems

from openapi_core.extensions.models.factories import ModelFactory
from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.exceptions import (
    InvalidSchemaValue, UndefinedSchemaProperty, MissingSchemaProperty,
    OpenAPISchemaError, NoOneOfSchema, MultipleOneOfSchema,
)
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
            enum=None, deprecated=False, all_of=None, one_of=None,
            additional_properties=None):
        self.type = schema_type and SchemaType(schema_type)
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
            for prop_name, val in all_properties.items()
            if prop_name in required
        )

    def get_all_required_properties_names(self):
        required = self.required.copy()

        for subschema in self.all_of:
            subschema_req = subschema.get_all_required_properties()
            required += subschema_req

        return set(required)

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
                raise InvalidSchemaValue("Null value for non-nullable schema")
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
            raise InvalidSchemaValue(
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
            raise InvalidSchemaValue(
                "Value of {0} not in enum choices: {1}".format(
                    value, self.enum)
            )

        return casted

    def _unmarshal_collection(self, value):
        return list(map(self.items.unmarshal, value))

    def _unmarshal_object(self, value):
        if not isinstance(value, (dict, )):
            raise InvalidSchemaValue(
                "Value of {0} not an object".format(value))

        if self.one_of:
            properties = None
            for one_of_schema in self.one_of:
                try:
                    found_props = self._unmarshal_properties(
                        value, one_of_schema)
                except OpenAPISchemaError:
                    pass
                else:
                    if properties is not None:
                        raise MultipleOneOfSchema(
                            "Exactly one schema should be valid,"
                            "multiple found")
                    properties = found_props

            if properties is None:
                raise NoOneOfSchema(
                    "Exactly one valid schema should be valid, None found.")

        else:
            properties = self._unmarshal_properties(value)

        return ModelFactory().create(properties, name=self.model)

    def _unmarshal_properties(self, value, one_of_schema=None):
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
        if extra_props and self.additional_properties is None:
            raise UndefinedSchemaProperty(
                "Undefined properties in schema: {0}".format(extra_props))

        properties = {}
        for prop_name in extra_props:
            prop_value = value[prop_name]
            properties[prop_name] = self.additional_properties.unmarshal(
                prop_value)

        for prop_name, prop in iteritems(all_props):
            try:
                prop_value = value[prop_name]
            except KeyError:
                if prop_name in all_req_props_names:
                    raise MissingSchemaProperty(
                        "Missing schema property {0}".format(prop_name))
                if not prop.nullable and not prop.default:
                    continue
                prop_value = prop.default
            properties[prop_name] = prop.unmarshal(prop_value)
        return properties
