"""OpenAPI core responses generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.media_types.generators import MediaTypeGenerator
from openapi_core.schema.parameters.generators import ParametersGenerator
from openapi_core.schema.responses.models import Response


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
