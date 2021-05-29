from typing import List

from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class ResponseFinderError(OpenAPIError):
    """Response finder error"""


@dataclass
class ResponseNotFound(ResponseFinderError):
    """Find response error"""
    http_status: int
    availableresponses: List[str]

    def __str__(self):
        return "Unknown response http status: {0}".format(
            str(self.http_status))
