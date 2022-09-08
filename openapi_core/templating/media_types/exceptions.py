from dataclasses import dataclass
from typing import List

from openapi_core.exceptions import OpenAPIError


class MediaTypeFinderError(OpenAPIError):
    """Media type finder error"""


@dataclass
class MediaTypeNotFound(MediaTypeFinderError):
    mimetype: str
    availableMimetypes: List[str]

    def __str__(self) -> str:
        return (
            f"Content for the following mimetype not found: {self.mimetype}. "
            f"Valid mimetypes: {self.availableMimetypes}"
        )
