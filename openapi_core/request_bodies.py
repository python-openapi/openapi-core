"""OpenAPI core requestBodies module"""
from openapi_core.media_types import MediaTypeGenerator


class RequestBody(object):
    """Represents an OpenAPI RequestBody."""

    def __init__(self, content, required=False):
        self.content = dict(content)
        self.required = required

    def __getitem__(self, content_type):
        return self.content[content_type]


class RequestBodyFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, request_body_spec):
        request_body_deref = self.dereferencer.dereference(
            request_body_spec)
        content = request_body_deref['content']
        media_types = self._generate_media_types(content)
        required = request_body_deref.get('required', False)
        return RequestBody(media_types, required=required)

    def _generate_media_types(self, content):
        return MediaTypeGenerator(self.dereferencer).generate(content)
