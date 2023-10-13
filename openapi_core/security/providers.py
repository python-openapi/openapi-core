import warnings
from typing import Any

from jsonschema_path import SchemaPath

from openapi_core.datatypes import RequestParameters
from openapi_core.security.exceptions import SecurityProviderError


class BaseProvider:
    def __init__(self, scheme: SchemaPath):
        self.scheme = scheme

    def __call__(self, parameters: RequestParameters) -> Any:
        raise NotImplementedError


class UnsupportedProvider(BaseProvider):
    def __call__(self, parameters: RequestParameters) -> Any:
        warnings.warn("Unsupported scheme type")


class ApiKeyProvider(BaseProvider):
    def __call__(self, parameters: RequestParameters) -> Any:
        name = self.scheme["name"]
        location = self.scheme["in"]
        source = getattr(parameters, location)
        if name not in source:
            raise SecurityProviderError("Missing api key parameter.")
        return source[name]


class HttpProvider(BaseProvider):
    def __call__(self, parameters: RequestParameters) -> Any:
        if "Authorization" not in parameters.header:
            raise SecurityProviderError("Missing authorization header.")
        auth_header = parameters.header["Authorization"]
        try:
            auth_type, encoded_credentials = auth_header.split(" ", 1)
        except ValueError:
            raise SecurityProviderError(
                "Could not parse authorization header."
            )

        scheme = self.scheme["scheme"]
        if auth_type.lower() != scheme:
            raise SecurityProviderError(
                f"Unknown authorization method {auth_type}"
            )

        return encoded_credentials
