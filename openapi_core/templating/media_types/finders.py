"""OpenAPI core templating media types finders module"""
import fnmatch

from openapi_core.spec import Spec
from openapi_core.templating.media_types.datatypes import MediaType
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound


class MediaTypeFinder:
    def __init__(self, content: Spec):
        self.content = content

    def find(self, mimetype: str) -> MediaType:
        if mimetype in self.content:
            return MediaType(self.content / mimetype, mimetype)

        if mimetype:
            for key, value in self.content.items():
                if fnmatch.fnmatch(mimetype, key):
                    return MediaType(value, key)

        raise MediaTypeNotFound(mimetype, list(self.content.keys()))
