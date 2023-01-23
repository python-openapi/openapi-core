import warnings
from dataclasses import dataclass
from typing import Iterable

from openapi_core.exceptions import OpenAPIError
from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.validation.exceptions import ValidationError
from openapi_core.validation.request.datatypes import Parameters


@dataclass
class ParametersError(Exception):
    parameters: Parameters
    errors: Iterable[OpenAPIError]

    @property
    def context(self) -> Iterable[OpenAPIError]:
        warnings.warn(
            "context property of ParametersError is deprecated. "
            "Use errors instead.",
            DeprecationWarning,
        )
        return self.errors


class RequestError(ValidationError):
    """Request error"""


class RequestBodyError(RequestError):
    def __str__(self) -> str:
        return "Request body error"


class InvalidRequestBody(RequestBodyError, ValidateError):
    """Invalid request body"""


class MissingRequestBodyError(RequestBodyError):
    """Missing request body error"""


class MissingRequestBody(MissingRequestBodyError):
    def __str__(self) -> str:
        return "Missing request body"


class MissingRequiredRequestBody(MissingRequestBodyError):
    def __str__(self) -> str:
        return "Missing required request body"


@dataclass
class ParameterError(RequestError):
    name: str
    location: str

    @classmethod
    def from_spec(cls, spec: Spec) -> "ParameterError":
        return cls(spec["name"], spec["in"])

    def __str__(self) -> str:
        return f"{self.location.title()} parameter error: {self.name}"


class InvalidParameter(ParameterError, ValidateError):
    def __str__(self) -> str:
        return f"Invalid {self.location} parameter: {self.name}"


class MissingParameterError(ParameterError):
    """Missing parameter error"""


class MissingParameter(MissingParameterError):
    def __str__(self) -> str:
        return f"Missing {self.location} parameter: {self.name}"


class MissingRequiredParameter(MissingParameterError):
    def __str__(self) -> str:
        return f"Missing required {self.location} parameter: {self.name}"


class SecurityError(RequestError):
    pass


class InvalidSecurity(SecurityError, ValidateError):
    """Invalid security"""
