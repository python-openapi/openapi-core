# -*- coding: utf-8 -*-
"""OpenAPI core operations models module"""
from six import iteritems
from openapi_spec_validator.validators import PathItemValidator

from openapi_core.compat import lru_cache
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.parameters.generators import ParametersGenerator
from openapi_core.schema.request_bodies.factories import RequestBodyFactory
from openapi_core.schema.responses.generators import ResponsesGenerator


class OperationsGenerator(object):
    """Represents an OpenAPI Operation in a service."""

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, path_name, path):
        path_deref = self.dereferencer.dereference(path)
        for http_method, operation in iteritems(path_deref):
            if http_method not in PathItemValidator.OPERATIONS:
                continue

            operation_deref = self.dereferencer.dereference(operation)
            responses_spec = operation_deref['responses']
            responses = self.responses_generator.generate(responses_spec)
            deprecated = operation_deref.get('deprecated', False)
            parameters_list = operation_deref.get('parameters', [])
            parameters = self.parameters_generator.generate_from_list(
                parameters_list)
            operation_id = operation_deref.get('operationId')
            tags_list = operation_deref.get('tags', [])

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
                    operation_id=operation_id, tags=list(tags_list)
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
