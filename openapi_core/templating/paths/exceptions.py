from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class PathError(OpenAPIError):
    """Path error"""


@dataclass
class PathNotFound(PathError):
    """Find path error"""
    url: str

    def __str__(self):
        return "Path not found for {0}".format(self.url)


@dataclass
class OperationNotFound(PathError):
    """Find path operation error"""
    url: str
    method: str

    def __str__(self):
        return "Operation {0} not found for {1}".format(
            self.method, self.url)


@dataclass
class ServerNotFound(PathError):
    """Find server error"""
    url: str

    def __str__(self):
        return "Server not found for {0}".format(self.url)
