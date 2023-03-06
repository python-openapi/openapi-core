from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterable

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.exceptions import ValidationError
from openapi_core.validation.schemas.exceptions import ValidateError


@dataclass
class HeadersError(Exception):
    headers: Dict[str, Any]
    context: Iterable[OpenAPIError]


class ResponseValidationError(ValidationError):
    """Response error"""


class DataValidationError(ResponseValidationError):
    """Data error"""


class InvalidData(DataValidationError, ValidateError):
    """Invalid data"""


class MissingData(DataValidationError):
    def __str__(self) -> str:
        return "Missing response data"


@dataclass
class HeaderValidationError(ResponseValidationError):
    name: str


class InvalidHeader(HeaderValidationError, ValidateError):
    """Invalid header"""


class MissingHeaderError(HeaderValidationError):
    """Missing header error"""


class MissingHeader(MissingHeaderError):
    def __str__(self) -> str:
        return f"Missing header (without default value): {self.name}"


class MissingRequiredHeader(MissingHeaderError):
    def __str__(self) -> str:
        return f"Missing required header: {self.name}"
