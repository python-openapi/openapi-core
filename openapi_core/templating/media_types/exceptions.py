from typing import List

from dataclasses import dataclass

from openapi_core.exceptions import OpenAPIError


class MediaTypeFinderError(OpenAPIError):
    """Media type finder error"""


@dataclass
class MediaTypeNotFound(MediaTypeFinderError):
    mimetype: str
    availableMimetypes: List[str]

    def __str__(self):
        return (
            "Content for the following mimetype not found: {}. "
            "Valid mimetypes: {}"
        ).format(self.mimetype, self.availableMimetypes)
