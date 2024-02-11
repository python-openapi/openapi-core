"""OpenAPI core templating media types finders module"""

import fnmatch
from typing import Mapping
from typing import Tuple

from jsonschema_path import SchemaPath

from openapi_core.templating.media_types.datatypes import MediaType
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound


class MediaTypeFinder:
    def __init__(self, content: SchemaPath):
        self.content = content

    def get_first(self) -> MediaType:
        mimetype, media_type = next(self.content.items())
        return MediaType(mimetype, {}, media_type)

    def find(self, mimetype: str) -> MediaType:
        if mimetype is None:
            raise MediaTypeNotFound(mimetype, list(self.content.keys()))

        mime_type, parameters = self._parse_mimetype(mimetype)

        # simple mime type
        for m in [mimetype, mime_type]:
            if m in self.content:
                return MediaType(mime_type, parameters, self.content / m)

        # range mime type
        if mime_type:
            for key, value in self.content.items():
                if fnmatch.fnmatch(mime_type, key):
                    return MediaType(key, parameters, value)

        raise MediaTypeNotFound(mimetype, list(self.content.keys()))

    def _parse_mimetype(self, mimetype: str) -> Tuple[str, Mapping[str, str]]:
        mimetype_parts = mimetype.split("; ")
        mime_type = mimetype_parts[0]
        parameters = {}
        if len(mimetype_parts) > 1:
            parameters_list = (
                param_str.split("=") for param_str in mimetype_parts[1:]
            )
            parameters = dict(parameters_list)
        return mime_type, parameters
