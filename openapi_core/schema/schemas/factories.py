"""OpenAPI core schemas factories module"""
import logging

from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.properties.generators import PropertiesGenerator
from openapi_core.schema.schemas.models import Schema
from openapi_core.schema.schemas.types import Contribution

log = logging.getLogger(__name__)


class SchemaFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, schema_spec):
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
        additional_properties_spec = schema_deref.get('additionalProperties',
                                                      True)
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

        properties = None
        if properties_spec:
            properties = self.properties_generator.generate(properties_spec)

        all_of = []
        if all_of_spec:
            all_of = list(map(self.create, all_of_spec))

        one_of = []
        if one_of_spec:
            one_of = list(map(self.create, one_of_spec))

        items = None
        if items_spec:
            items = self._create_items(items_spec)

        additional_properties = additional_properties_spec
        if isinstance(additional_properties_spec, dict):
            additional_properties = self.create(additional_properties_spec)

        return Schema(
            schema_type=schema_type, model=model, properties=properties,
            items=items, schema_format=schema_format, required=required,
            default=default, nullable=nullable, enum=enum,
            deprecated=deprecated, all_of=all_of, one_of=one_of,
            additional_properties=additional_properties,
            min_items=min_items, max_items=max_items, min_length=min_length,
            max_length=max_length, pattern=pattern, unique_items=unique_items,
            minimum=minimum, maximum=maximum, multiple_of=multiple_of,
            exclusive_maximum=exclusive_maximum,
            exclusive_minimum=exclusive_minimum,
            min_properties=min_properties, max_properties=max_properties,
            _source=schema_deref,
        )

    @property
    @lru_cache()
    def properties_generator(self):
        return PropertiesGenerator(self.dereferencer, self)

    def _create_items(self, items_spec):
        return self.create(items_spec)


class SchemaDictFactory(object):

    contributions = (
        Contribution('type', src_prop_attr='value'),
        Contribution('format'),
        Contribution('properties', is_dict=True, dest_default={}),
        Contribution('required', dest_default=[]),
        Contribution('default'),
        Contribution('nullable', dest_default=False),
        Contribution('all_of', dest_prop_name='allOf', is_list=True, dest_default=[]),
        Contribution('one_of', dest_prop_name='oneOf', is_list=True, dest_default=[]),
        Contribution('additional_properties', dest_prop_name='additionalProperties', dest_default=True),
        Contribution('min_items', dest_prop_name='minItems'),
        Contribution('max_items', dest_prop_name='maxItems'),
        Contribution('min_length', dest_prop_name='minLength'),
        Contribution('max_length', dest_prop_name='maxLength'),
        Contribution('pattern', src_prop_attr='pattern'),
        Contribution('unique_items', dest_prop_name='uniqueItems', dest_default=False),
        Contribution('minimum'),
        Contribution('maximum'),
        Contribution('multiple_of', dest_prop_name='multipleOf'),
        Contribution('exclusive_minimum', dest_prop_name='exclusiveMinimum', dest_default=False),
        Contribution('exclusive_maximum', dest_prop_name='exclusiveMaximum', dest_default=False),
        Contribution('min_properties', dest_prop_name='minProperties'),
        Contribution('max_properties', dest_prop_name='maxProperties'),
    )

    def create(self, schema):
        schema_dict = {}
        for contrib in self.contributions:
            self._contribute(schema, schema_dict, contrib)
        return schema_dict

    def _contribute(self, schema, schema_dict, contrib):
        def src_map(x):
            return getattr(x, '__dict__')
        src_val = getattr(schema, contrib.src_prop_name)

        if src_val and contrib.src_prop_attr:
            src_val = getattr(src_val, contrib.src_prop_attr)

        if contrib.is_list:
            src_val = list(map(src_map, src_val))
        if contrib.is_dict:
            src_val = dict(
                (k, src_map(v))
                for k, v in iteritems(src_val)
            )

        if src_val == contrib.dest_default:
            return

        dest_prop_name = contrib.dest_prop_name or contrib.src_prop_name
        schema_dict[dest_prop_name] = src_val
