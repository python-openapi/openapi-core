"""OpenAPI core schemas module"""
import logging
from distutils.util import strtobool
from collections import defaultdict

from json import loads
from six import iteritems

log = logging.getLogger(__name__)

DEFAULT_CAST_CALLABLE_GETTER = {
    'integer': int,
    'number': float,
    'boolean': lambda x: bool(strtobool(x)),
    'object': loads,
}


class Schema(object):
    """Represents an OpenAPI Schema."""

    def __init__(
            self, schema_type, properties=None, items=None, spec_format=None,
            required=False):
        self.type = schema_type
        self.properties = properties and dict(properties) or {}
        self.items = items
        self.format = spec_format
        self.required = required

    def __getitem__(self, name):
        return self.properties[name]

    def get_cast_mapping(self):
        mapping = DEFAULT_CAST_CALLABLE_GETTER.copy()
        if self.items:
            mapping.update({
                'array': lambda x: list(map(self.items.unmarshal, x)),
            })

        return defaultdict(lambda: lambda x: x, mapping)

    def cast(self, value):
        """Cast value to schema type"""
        if value is None:
            return None

        cast_mapping = self.get_cast_mapping()

        if self.type in cast_mapping and value == '':
            return None

        cast_callable = cast_mapping[self.type]
        try:
            return cast_callable(value)
        except ValueError:
            log.warning(
                "Failed to cast value of %s to %s", value, self.type,
            )
            return value

    def unmarshal(self, value):
        """Unmarshal parameter from the value."""
        casted = self.cast(value)

        if casted is None and not self.required:
            return None

        return casted


class PropertiesGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, properties):
        for property_name, schema_spec in iteritems(properties):
            schema = self._create_schema(schema_spec)
            yield property_name, schema

    def _create_schema(self, schema_spec):
        return SchemaFactory(self.dereferencer).create(schema_spec)


class SchemaFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, schema_spec):
        schema_deref = self.dereferencer.dereference(schema_spec)
        schema_type = schema_deref['type']
        required = schema_deref.get('required', False)
        properties_spec = schema_deref.get('properties', None)
        items_spec = schema_deref.get('items', None)

        properties = None
        if properties_spec:
            properties = self._generate_properties(properties_spec)

        items = None
        if items_spec:
            items = self._create_items(items_spec)

        return Schema(
            schema_type, properties=properties, items=items, required=required)

    def _generate_properties(self, properties_spec):
        return PropertiesGenerator(self.dereferencer).generate(properties_spec)

    def _create_items(self, items_spec):
        return SchemaFactory(self.dereferencer).create(items_spec)
