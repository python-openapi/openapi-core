from dataclasses import dataclass
from typing import Iterable

from openapi_core.datatypes import Parameters
from openapi_core.exceptions import OpenAPIError
from openapi_core.spec import Spec
from openapi_core.validation.exceptions import ValidationError
from openapi_core.validation.schemas.exceptions import ValidateError


@dataclass
class ParametersError(Exception):
    parameters: Parameters
    errors: Iterable[OpenAPIError]


class RequestValidationError(ValidationError):
    """Request validation error"""


class RequestBodyValidationError(RequestValidationError):
    def __str__(self) -> str:
        return "Request body validation error"


class InvalidRequestBody(RequestBodyValidationError, ValidateError):
    """Invalid request body"""


class MissingRequestBodyError(RequestBodyValidationError):
    """Missing request body error"""


class MissingRequestBody(MissingRequestBodyError):
    def __str__(self) -> str:
        return "Missing request body"


class MissingRequiredRequestBody(MissingRequestBodyError):
    def __str__(self) -> str:
        return "Missing required request body"


@dataclass
class ParameterValidationError(RequestValidationError):
    name: str
    location: str

    @classmethod
    def from_spec(cls, spec: Spec) -> "ParameterValidationError":
        return cls(spec["name"], spec["in"])

    def __str__(self) -> str:
        return f"{self.location.title()} parameter error: {self.name}"


class InvalidParameter(ParameterValidationError, ValidateError):
    def __str__(self) -> str:
        return f"Invalid {self.location} parameter: {self.name}"


class MissingParameterError(ParameterValidationError):
    """Missing parameter error"""


class MissingParameter(MissingParameterError):
    def __str__(self) -> str:
        return f"Missing {self.location} parameter: {self.name}"


class MissingRequiredParameter(MissingParameterError):
    def __str__(self) -> str:
        return f"Missing required {self.location} parameter: {self.name}"


class SecurityValidationError(RequestValidationError):
    pass


class InvalidSecurity(SecurityValidationError, ValidateError):
    """Invalid security"""
