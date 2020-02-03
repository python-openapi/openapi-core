"""OpenAPI core parameters models module"""
import logging

from openapi_core.schema.parameters.enums import (
    ParameterLocation, ParameterStyle,
)
from openapi_core.schema.schemas.enums import SchemaType

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
