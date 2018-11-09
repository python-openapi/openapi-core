"""OpenAPI core schemas factories module"""
import logging

from openapi_core.compat import lru_cache
from openapi_core.schema.properties.generators import PropertiesGenerator
from openapi_core.schema.schemas.models import Schema

log = logging.getLogger(__name__)


class SchemaFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer
        self.seen = {}

    def create(self, schema_spec):
        if isinstance(schema_spec, dict) and '$ref' in schema_spec and schema_spec['$ref'] in self.seen:
            return self.seen[schema_spec['$ref']]

        schema_deref = self.dereferencer.dereference(schema_spec)

        schema_type = schema_deref.get('type', None)
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
        min_items = schema_deref.get('minItems', None)
        max_items = schema_deref.get('maxItems', None)
        min_length = schema_deref.get('minLength', None)
        max_length = schema_deref.get('maxLength', None)
        pattern = schema_deref.get('pattern', None)
        unique_items = schema_deref.get('uniqueItems', None)
        minimum = schema_deref.get('minimum', None)
        maximum = schema_deref.get('maximum', None)
        multiple_of = schema_deref.get('multipleOf', None)
        exclusive_minimum = schema_deref.get('exclusiveMinimum', False)
        exclusive_maximum = schema_deref.get('exclusiveMaximum', False)
        min_properties = schema_deref.get('minProperties', None)
        max_properties = schema_deref.get('maxProperties', None)

        schema = Schema(
            schema_type=schema_type,
            model=model,
            schema_format=schema_format,
            required=required,
            default=default,
            nullable=nullable,
            enum=enum,
            deprecated=deprecated,
            min_items=min_items,
            max_items=max_items,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            unique_items=unique_items,
            minimum=minimum,
            maximum=maximum,
            multiple_of=multiple_of,
            exclusive_maximum=exclusive_maximum,
            exclusive_minimum=exclusive_minimum,
            min_properties=min_properties,
            max_properties=max_properties,
        )

        if isinstance(schema_spec, dict) and '$ref' in schema_spec:
            self.seen[schema_spec['$ref']] = schema

        if properties_spec:
            schema.properties = dict(self.properties_generator.generate(properties_spec))

        if all_of_spec:
            schema.all_of = list(map(self.create, all_of_spec))

        if one_of_spec:
            schema.one_of = list(map(self.create, one_of_spec))

        if items_spec:
            schema.items = self._create_items(items_spec)

        if additional_properties_spec:
            schema.additional_properties = self.create(additional_properties_spec)

        return schema

    @property
    @lru_cache()
    def properties_generator(self):
        return PropertiesGenerator(self.dereferencer, self)

    def _create_items(self, items_spec):
        return self.create(items_spec)
