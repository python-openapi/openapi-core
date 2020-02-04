"""OpenAPI core security schemes models module"""
from openapi_core.schema.security_schemes.enums import (
    SecuritySchemeType, ApiKeyLocation, HttpAuthScheme,
)


class SecurityScheme(object):
    """Represents an OpenAPI Security Scheme."""

    def __init__(
            self, scheme_type, description=None, name=None, apikey_in=None,
            scheme=None, bearer_format=None, flows=None,
            open_id_connect_url=None,
    ):
        self.type = SecuritySchemeType(scheme_type)
        self.description = description
        self.name = name
        self.apikey_in = apikey_in and ApiKeyLocation(apikey_in)
        self.scheme = scheme and HttpAuthScheme(scheme)
        self.bearer_format = bearer_format
        self.flows = flows
        self.open_id_connect_url = open_id_connect_url
