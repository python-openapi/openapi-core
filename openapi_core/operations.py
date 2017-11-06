# -*- coding: utf-8 -*-
"""OpenAPI core operations module"""
import logging
from functools import lru_cache

from six import iteritems

from openapi_core.exceptions import InvalidResponse
from openapi_core.parameters import ParametersGenerator
from openapi_core.request_bodies import RequestBodyFactory
from openapi_core.responses import ResponsesGenerator

log = logging.getLogger(__name__)


class Operation(object):
    """Represents an OpenAPI Operation."""

    def __init__(
            self, http_method, path_name, responses, parameters,
            request_body=None, deprecated=False, operation_id=None):
        self.http_method = http_method
        self.path_name = path_name
        self.responses = dict(responses)
        self.parameters = dict(parameters)
        self.request_body = request_body
        self.deprecated = deprecated
        self.operation_id = operation_id

    def __getitem__(self, name):
        return self.parameters[name]

    def get_response(self, http_status='default'):
        try:
            return self.responses[http_status]
        except KeyError:
            # try range
            http_status_range = '{0}XX'.format(http_status[0])
            if http_status_range in self.responses:
                return self.responses[http_status_range]

            if 'default' not in self.responses:
                raise InvalidResponse(
                    "Unknown response http status {0}".format(http_status))

            return self.responses['default']


class OperationsGenerator(object):
    """Represents an OpenAPI Operation in a service."""

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, path_name, path):
        path_deref = self.dereferencer.dereference(path)
        for http_method, operation in iteritems(path_deref):
            if http_method.startswith('x-') or http_method == 'parameters':
                continue

            operation_deref = self.dereferencer.dereference(operation)
            responses_spec = operation_deref['responses']
            responses = self.responses_generator.generate(responses_spec)
            deprecated = operation_deref.get('deprecated', False)
            parameters_list = operation_deref.get('parameters', [])
            parameters = self.parameters_generator.generate_from_list(
                parameters_list)

            request_body = None
            if 'requestBody' in operation_deref:
                request_body_spec = operation_deref.get('requestBody')
                request_body = self.request_body_factory.create(
                    request_body_spec)

            yield (
                http_method,
                Operation(
                    http_method, path_name, responses, list(parameters),
                    request_body=request_body, deprecated=deprecated,
                ),
            )

    @property
    @lru_cache()
    def responses_generator(self):
        return ResponsesGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def parameters_generator(self):
        return ParametersGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def request_body_factory(self):
        return RequestBodyFactory(self.dereferencer, self.schemas_registry)
