"""OpenAPI core schemas factories module"""
import logging

from openapi_core.compat import lru_cache
from openapi_core.schema.properties.generators import PropertiesGenerator
from openapi_core.schema.schemas.models import Schema

log = logging.getLogger(__name__)


class SchemaFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, schema_spec):
        schema_deref = self.dereferencer.dereference(schema_spec)

        schema_type = schema_deref.get('type')
        schema_format = schema_deref.get('format')
        model = schema_deref.get('x-model', None)
        required = schema_deref.get('required', False)
        default = schema_deref.get('default', None)
        properties_spec = schema_deref.get('properties', None)
        items_spec = schema_deref.get('items', None)
        nullable = schema_deref.get('nullable', False)
        enum = schema_deref.get('enum', None)
        deprecated = schema_deref.get('deprecated', False)
        all_of_spec = schema_deref.get('allOf', None)
        one_of_spec = schema_deref.get('oneOf', None)
        additional_properties_spec = schema_deref.get('additionalProperties')

        properties = None
        if properties_spec:
            properties = self.properties_generator.generate(properties_spec)

        all_of = []
        if all_of_spec:
            all_of = map(self.create, all_of_spec)

        one_of = []
        if one_of_spec:
            one_of = map(self.create, one_of_spec)

        items = None
        if items_spec:
            items = self._create_items(items_spec)

        additional_properties = None
        if additional_properties_spec:
            additional_properties = self.create(additional_properties_spec)

        return Schema(
            schema_type=schema_type, model=model, properties=properties,
            items=items, schema_format=schema_format, required=required,
            default=default, nullable=nullable, enum=enum,
            deprecated=deprecated, all_of=all_of, one_of=one_of,
            additional_properties=additional_properties,
        )

    @property
    @lru_cache()
    def properties_generator(self):
        return PropertiesGenerator(self.dereferencer, self)

    def _create_items(self, items_spec):
        return self.create(items_spec)
