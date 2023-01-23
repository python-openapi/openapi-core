from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterable

from openapi_core.exceptions import OpenAPIError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.validation.exceptions import ValidationError


@dataclass
class HeadersError(Exception):
    headers: Dict[str, Any]
    context: Iterable[OpenAPIError]


class ResponseError(ValidationError):
    """Response error"""


class DataError(ResponseError):
    """Data error"""


class InvalidData(DataError, ValidateError):
    """Invalid data"""


class MissingData(DataError):
    def __str__(self) -> str:
        return "Missing response data"


@dataclass
class HeaderError(ResponseError):
    name: str


class InvalidHeader(HeaderError, ValidateError):
    """Invalid header"""


class MissingHeaderError(HeaderError):
    """Missing header error"""


class MissingHeader(MissingHeaderError):
    def __str__(self) -> str:
        return f"Missing header (without default value): {self.name}"


class MissingRequiredHeader(MissingHeaderError):
    def __str__(self) -> str:
        return f"Missing required header: {self.name}"
