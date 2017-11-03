"""OpenAPI core parameters module"""
import logging
import warnings

from openapi_core.exceptions import (
    EmptyValue, InvalidValueType, InvalidParameterValue,
)

log = logging.getLogger(__name__)


class Parameter(object):
    """Represents an OpenAPI operation Parameter."""

    def __init__(
            self, name, location, schema=None, required=False,
            deprecated=False, allow_empty_value=False,
            items=None, collection_format=None):
        self.name = name
        self.location = location
        self.schema = schema
        self.required = True if self.location == "path" else required
        self.deprecated = deprecated
        self.allow_empty_value = (
            allow_empty_value if self.location == "query" else False
        )
        self.items = items
        self.collection_format = collection_format

    def unmarshal(self, value):
        if self.deprecated:
            warnings.warn(
                "{0} parameter is deprecated".format(self.name),
                DeprecationWarning,
            )

        if (self.location == "query" and value == "" and
                not self.allow_empty_value):
            raise EmptyValue(
                "Value of {0} parameter cannot be empty".format(self.name))

        if not self.schema:
            return value

        try:
            return self.schema.unmarshal(value)
        except InvalidValueType as exc:
            raise InvalidParameterValue(str(exc))


class ParametersGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, paramters):
        for parameter in paramters:
            parameter_deref = self.dereferencer.dereference(parameter)

            allow_empty_value = parameter_deref.get('allowEmptyValue')
            required = parameter_deref.get('required', False)

            schema_spec = parameter_deref.get('schema', None)
            schema = None
            if schema_spec:
                schema, _ = self.schemas_registry.get_or_create(schema_spec)

            yield (
                parameter_deref['name'],
                Parameter(
                    parameter_deref['name'], parameter_deref['in'],
                    schema=schema, required=required,
                    allow_empty_value=allow_empty_value,
                ),
            )
