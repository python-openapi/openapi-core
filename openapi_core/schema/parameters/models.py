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
from openapi_core.schema.schemas.exceptions import InvalidSchemaValue

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

        try:
            raw = location[self.name]
        except KeyError:
            if self.required:
                raise MissingRequiredParameter(
                    "Missing required `{0}` parameter".format(self.name))

            if not self.schema or self.schema.default is None:
                raise MissingParameter(
                    "Missing `{0}` parameter".format(self.name))

            raw = self.schema.default

        if self.aslist and self.explode:
            return location.getlist(self.name)

        return raw

    def unmarshal(self, value):
        if self.deprecated:
            warnings.warn(
                "{0} parameter is deprecated".format(self.name),
                DeprecationWarning,
            )

        if (self.location == ParameterLocation.QUERY and value == "" and
                not self.allow_empty_value):
            raise EmptyParameterValue(
                "Value of {0} parameter cannot be empty".format(self.name))

        if not self.schema:
            return value

        deserialized = self.deserialize(value)

        try:
            return self.schema.unmarshal(deserialized)
        except InvalidSchemaValue as exc:
            raise InvalidParameterValue(str(exc))
