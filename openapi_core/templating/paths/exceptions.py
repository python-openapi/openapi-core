from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class PathError(OpenAPIError):
    """Path error"""


@dataclass
class PathNotFound(PathError):
    """Path not found"""

    url: str

    def __str__(self) -> str:
        return f"Path not found for {self.url}"


@dataclass
class PathsNotFound(PathNotFound):
    """Paths not found"""

    def __str__(self) -> str:
        return f"Paths not found in spec: {self.url}"


@dataclass
class OperationNotFound(PathError):
    """Find path operation error"""

    url: str
    method: str

    def __str__(self) -> str:
        return f"Operation {self.method} not found for {self.url}"


@dataclass
class ServerNotFound(PathError):
    """Find server error"""

    url: str

    def __str__(self) -> str:
        return f"Server not found for {self.url}"
