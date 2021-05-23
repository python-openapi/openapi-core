"""OpenAPI core templating media types finders module"""
import fnmatch

from openapi_core.spec.paths import SpecPath
from openapi_core.templating.media_types.datatypes import MediaTypeResult
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound


class MediaTypeFinder:

    def __init__(self, content: SpecPath):
        self.content = content

    def find(self, request) -> MediaTypeResult:
        if request.mimetype in self.content:
            media_type = self.content / request.mimetype
            return MediaTypeResult(media_type, request.mimetype)

        for key, value in self.content.items():
            if fnmatch.fnmatch(request.mimetype, key):
                return MediaTypeResult(value, key)

        raise MediaTypeNotFound(request.mimetype, list(self.content.keys()))
