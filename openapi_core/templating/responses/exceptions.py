from dataclasses import dataclass
from typing import List

from openapi_core.exceptions import OpenAPIError


class ResponseFinderError(OpenAPIError):
    """Response finder error"""


@dataclass
class ResponseNotFound(ResponseFinderError):
    """Find response error"""

    http_status: str
    availableresponses: List[str]

    def __str__(self) -> str:
        return f"Unknown response http status: {str(self.http_status)}"
