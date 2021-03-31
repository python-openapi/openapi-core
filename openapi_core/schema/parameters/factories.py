"""OpenAPI core parameters factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.content.factories import ContentFactory
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.parameters.models import Parameter


class ParameterFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, parameter_spec, parameter_name=None):
        parameter_deref = self.dereferencer.dereference(parameter_spec)

        parameter_name = parameter_name or parameter_deref['name']
        parameter_in = parameter_deref.get('in', 'header')

        allow_empty_value = parameter_deref.get('allowEmptyValue')
        required = parameter_deref.get('required', False)

        style = parameter_deref.get('style')
        explode = parameter_deref.get('explode')

        schema_spec = parameter_deref.get('schema', None)
        schema = None
        if schema_spec:
            schema, _ = self.schemas_registry.get_or_create(schema_spec)

        content_spec = parameter_deref.get('content', None)
        content = None
        if content_spec:
            content = self.content_factory.create(content_spec)

        extensions = self.extensions_generator.generate(parameter_deref)

        return Parameter(
            parameter_name, parameter_in,
            schema=schema, required=required,
            allow_empty_value=allow_empty_value,
            style=style, explode=explode, content=content,
            extensions=extensions,
        )

    @property
    @lru_cache()
    def content_factory(self):
        return ContentFactory(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
