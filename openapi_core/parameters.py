"""OpenAPI core parameters module"""
import logging

log = logging.getLogger(__name__)


class Parameter(object):
    """Represents an OpenAPI operation Parameter."""

    def __init__(
            self, name, location, schema=None, default=None,
            required=False, deprecated=False, allow_empty_value=False,
            items=None, collection_format=None):
        self.name = name
        self.location = location
        self.schema = schema
        self.default = default
        self.required = required
        self.deprecated = deprecated
        self.allow_empty_value = allow_empty_value
        self.items = items
        self.collection_format = collection_format

    def unmarshal(self, value):
        if not self.schema:
            return value

        return self.schema.unmarshal(value)


class ParametersGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, paramters):
        for parameter in paramters:
            parameter_deref = self.dereferencer.dereference(parameter)

            default = parameter_deref.get('default')
            required = parameter_deref.get('required', False)

            schema_spec = parameter_deref.get('schema', None)
            schema = None
            if schema_spec:
                schema, _ = self.schemas_registry.get_or_create(schema_spec)

            yield (
                parameter_deref['name'],
                Parameter(
                    parameter_deref['name'], parameter_deref['in'],
                    schema=schema, default=default, required=required,
                ),
            )
