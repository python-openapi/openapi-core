"""OpenAPI core templating media types finders module"""
import fnmatch

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound


class MediaTypeFinder:
    def __init__(self, content):
        self.content = content

    def find(self, mimetype):
        if mimetype in self.content:
            return self.content / mimetype, mimetype

        if mimetype:
            for key, value in self.content.items():
                if fnmatch.fnmatch(mimetype, key):
                    return value, key

        raise MediaTypeNotFound(mimetype, list(self.content.keys()))
