import warnings
from dataclasses import dataclass
from typing import Iterable

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.protocols import Request


@dataclass
class ParametersError(Exception):
    parameters: Parameters
    errors: Iterable[Exception]

    @property
    def context(self) -> Iterable[Exception]:
        warnings.warn(
            "context property of ParametersError is deprecated. "
            "Use errors instead.",
            DeprecationWarning,
        )
        return self.errors


class OpenAPIRequestBodyError(OpenAPIError):
    pass


class MissingRequestBodyError(OpenAPIRequestBodyError):
    """Missing request body error"""


class MissingRequestBody(MissingRequestBodyError):
    def __str__(self) -> str:
        return "Missing request body"


class MissingRequiredRequestBody(MissingRequestBodyError):
    def __str__(self) -> str:
        return "Missing required request body"
