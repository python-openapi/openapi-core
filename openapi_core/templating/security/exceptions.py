from dataclasses import dataclass
from typing import List

from openapi_core.exceptions import OpenAPIError


class SecurityFinderError(OpenAPIError):
    """Security finder error"""


@dataclass
class SecurityNotFound(SecurityFinderError):
    """Find security error"""

    schemes: List[List[str]]

    def __str__(self) -> str:
        return f"Security not found. Schemes not valid for any requirement: {str(self.schemes)}"
