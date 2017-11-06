"""OpenAPI core responses module"""
from functools import lru_cache

from six import iteritems

from openapi_core.exceptions import InvalidContentType
from openapi_core.media_types import MediaTypeGenerator
from openapi_core.parameters import ParametersGenerator


class Response(object):

    def __init__(
            self, http_status, description, headers=None, content=None,
            links=None):
        self.http_status = http_status
        self.description = description
        self.headers = headers and dict(headers) or {}
        self.content = content and dict(content) or {}
        self.links = links and dict(links) or {}

    def __getitem__(self, mimetype):
        try:
            return self.content[mimetype]
        except KeyError:
            raise InvalidContentType(
                "Invalid mime type `{0}`".format(mimetype))


class ResponsesGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, responses):
        for http_status, response in iteritems(responses):
            response_deref = self.dereferencer.dereference(response)
            description = response_deref['description']
            headers = response_deref.get('headers')
            content = response_deref.get('content')

            media_types = None
            if content:
                media_types = self.media_types_generator.generate(content)

            parameters = None
            if headers:
                parameters = self.parameters_generator.generate(headers)

            yield http_status, Response(
                http_status, description,
                content=media_types, headers=parameters)

    @property
    @lru_cache()
    def media_types_generator(self):
        return MediaTypeGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def parameters_generator(self):
        return ParametersGenerator(self.dereferencer, self.schemas_registry)
