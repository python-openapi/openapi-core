"""OpenAPI core parameters factories module"""
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

        return Parameter(
            parameter_name, parameter_in,
            schema=schema, required=required,
            allow_empty_value=allow_empty_value,
            style=style, explode=explode,
        )
