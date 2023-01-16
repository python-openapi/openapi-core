from dataclasses import dataclass
from typing import Iterable

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.protocols import Request


@dataclass
class ParametersError(Exception):
    parameters: Parameters
    context: Iterable[Exception]


class OpenAPIRequestBodyError(OpenAPIError):
    pass


class MissingRequestBodyError(OpenAPIRequestBodyError):
    """Missing request body error"""


@dataclass
class MissingRequestBody(MissingRequestBodyError):
    request: Request

    def __str__(self) -> str:
        return "Missing request body"


@dataclass
class MissingRequiredRequestBody(MissingRequestBodyError):
    request: Request

    def __str__(self) -> str:
        return "Missing required request body"
