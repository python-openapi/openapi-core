from dataclasses import dataclass
from typing import List

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.protocols import Request


@dataclass
class ParametersError(Exception):
    parameters: Parameters
    context: List[Exception]


class OpenAPIRequestBodyError(OpenAPIError):
    pass


class MissingRequestBodyError(OpenAPIRequestBodyError):
    """Missing request body error"""


@dataclass
class MissingRequestBody(MissingRequestBodyError):
    request: Request

    def __str__(self):
        return "Missing request body"


@dataclass
class MissingRequiredRequestBody(MissingRequestBodyError):
    request: Request

    def __str__(self):
        return "Missing required request body"
