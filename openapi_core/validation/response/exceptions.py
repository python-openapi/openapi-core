from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterable

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.response.protocols import Response


@dataclass
class HeadersError(Exception):
    headers: Dict[str, Any]
    context: Iterable[OpenAPIError]


class OpenAPIResponseError(OpenAPIError):
    pass


@dataclass
class MissingResponseContent(OpenAPIResponseError):
    response: Response

    def __str__(self) -> str:
        return "Missing response content"
