"""OpenAPI core parameters models module"""
import logging
import warnings

from openapi_core.schema.parameters.enums import (
    ParameterLocation, ParameterStyle,
)
from openapi_core.schema.parameters.exceptions import (
    MissingRequiredParameter, MissingParameter, InvalidParameterValue,
    EmptyParameterValue,
)
from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.exceptions import OpenAPISchemaError

log = logging.getLogger(__name__)


class Parameter(object):
    """Represents an OpenAPI operation Parameter."""

    PARAMETER_STYLE_DESERIALIZERS = {
        ParameterStyle.FORM: lambda x: x.split(','),
        ParameterStyle.SIMPLE: lambda x: x.split(','),
        ParameterStyle.SPACE_DELIMITED: lambda x: x.split(' '),
        ParameterStyle.PIPE_DELIMITED: lambda x: x.split('|'),
    }

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
        self.explode = self.default_explode if explode is None else explode

    @property
    def aslist(self):
        return (
            self.schema and
            self.schema.type in [SchemaType.ARRAY, SchemaType.OBJECT]
        )

    @property
    def default_style(self):
        simple_locations = [ParameterLocation.PATH, ParameterLocation.HEADER]
        return (
            'simple' if self.location in simple_locations else "form"
        )

    @property
    def default_explode(self):
        return self.style == ParameterStyle.FORM

    def get_dererializer(self):
        return self.PARAMETER_STYLE_DESERIALIZERS[self.style]

    def deserialize(self, value):
        if not self.aslist or self.explode:
            return value

        deserializer = self.get_dererializer()
        return deserializer(value)

    def get_value(self, request):
        location = request.parameters[self.location.value]

        if self.name not in location:
            if self.required:
                raise MissingRequiredParameter(self.name)

            if not self.schema or self.schema.default is None:
                raise MissingParameter(self.name)

            return self.schema.default

        if self.aslist and self.explode:
            return location.getlist(self.name)

        return location[self.name]

    def unmarshal(self, value, custom_formatters=None):
        if self.deprecated:
            warnings.warn(
                "{0} parameter is deprecated".format(self.name),
                DeprecationWarning,
            )

        if (self.location == ParameterLocation.QUERY and value == "" and
                not self.allow_empty_value):
            raise EmptyParameterValue(self.name)

        if not self.schema:
            return value

        try:
            deserialized = self.deserialize(value)
        except (ValueError, AttributeError) as exc:
            raise InvalidParameterValue(self.name, exc)

        try:
            unmarshalled = self.schema.unmarshal(
                deserialized,
                custom_formatters=custom_formatters,
                strict=False,
            )
        except OpenAPISchemaError as exc:
            raise InvalidParameterValue(self.name, exc)

        try:
            return self.schema.validate(unmarshalled, custom_formatters=custom_formatters)
        except OpenAPISchemaError as exc:
            raise InvalidParameterValue(self.name, exc)
