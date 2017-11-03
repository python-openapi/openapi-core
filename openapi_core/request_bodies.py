"""OpenAPI core requestBodies module"""
from functools import lru_cache

from openapi_core.exceptions import InvalidContentType
from openapi_core.media_types import MediaTypeGenerator


class RequestBody(object):
    """Represents an OpenAPI RequestBody."""

    def __init__(self, content, required=False):
        self.content = dict(content)
        self.required = required

    def __getitem__(self, mimetype):
        try:
            return self.content[mimetype]
        except KeyError:
            raise InvalidContentType(
                "Invalid mime type `{0}`".format(mimetype))


class RequestBodyFactory(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def create(self, request_body_spec):
        request_body_deref = self.dereferencer.dereference(
            request_body_spec)
        content = request_body_deref['content']
        media_types = self.media_types_generator.generate(content)
        required = request_body_deref.get('required', False)
        return RequestBody(media_types, required=required)

    @property
    @lru_cache()
    def media_types_generator(self):
        return MediaTypeGenerator(self.dereferencer, self.schemas_registry)
