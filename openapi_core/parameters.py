"""OpenAPI core parameters module"""
import logging
import warnings

from six import iteritems

from openapi_core.enums import ParameterLocation, ParameterStyle
from openapi_core.exceptions import (
    EmptyValue, InvalidValueType, InvalidParameterValue,
)

log = logging.getLogger(__name__)


class Parameter(object):
    """Represents an OpenAPI operation Parameter."""

    def __init__(
            self, name, location, schema=None, required=False,
            deprecated=False, allow_empty_value=False,
            items=None, style=None, explode=None):
        self.name = name
        self.location = ParameterLocation(location)
        self.schema = schema
        self.required = (
            True if self.location == ParameterLocation.PATH else required
        )
        self.deprecated = deprecated
        self.allow_empty_value = (
            allow_empty_value if self.location == ParameterLocation.QUERY
            else False
        )
        self.items = items
        self.style = ParameterStyle(style or self.default_style)
        self.explode = explode or self.default_explode

    @property
    def default_style(self):
        simple_locations = [ParameterLocation.PATH, ParameterLocation.HEADER]
        return (
            'simple' if self.location in simple_locations else "form"
        )

    @property
    def default_explode(self):
        return self.style == ParameterStyle.FORM

    def unmarshal(self, value):
        if self.deprecated:
            warnings.warn(
                "{0} parameter is deprecated".format(self.name),
                DeprecationWarning,
            )

        if (self.location == ParameterLocation.QUERY and value == "" and
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

    def generate(self, parameters):
        for parameter_name, parameter in iteritems(parameters):
            parameter_deref = self.dereferencer.dereference(parameter)

            parameter_in = parameter_deref.get('in', 'header')

            allow_empty_value = parameter_deref.get('allowEmptyValue')
            required = parameter_deref.get('required', False)

            schema_spec = parameter_deref.get('schema', None)
            schema = None
            if schema_spec:
                schema, _ = self.schemas_registry.get_or_create(schema_spec)

            yield (
                parameter_name,
                Parameter(
                    parameter_name, parameter_in,
                    schema=schema, required=required,
                    allow_empty_value=allow_empty_value,
                ),
            )

    def generate_from_list(self, parameters_list):
        for parameter in parameters_list:
            parameter_deref = self.dereferencer.dereference(parameter)

            parameter_name = parameter_deref['name']
            parameter_in = parameter_deref.get('in', 'header')

            allow_empty_value = parameter_deref.get('allowEmptyValue')
            required = parameter_deref.get('required', False)

            style = parameter_deref.get('style')
            explode = parameter_deref.get('explode')

            schema_spec = parameter_deref.get('schema', None)
            schema = None
            if schema_spec:
                schema, _ = self.schemas_registry.get_or_create(schema_spec)

            yield (
                parameter_name,
                Parameter(
                    parameter_name, parameter_in,
                    schema=schema, required=required,
                    allow_empty_value=allow_empty_value,
                    style=style, explode=explode,
                ),
            )
