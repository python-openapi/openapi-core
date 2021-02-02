# -*- coding: utf-8 -*-
"""OpenAPI core operations models module"""
from six import iteritems
from openapi_spec_validator.validators import PathItemValidator

from openapi_core.compat import lru_cache
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.external_docs.factories import (
    ExternalDocumentationFactory,
)
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.parameters.generators import ParametersGenerator
from openapi_core.schema.request_bodies.factories import RequestBodyFactory
from openapi_core.schema.responses.generators import ResponsesGenerator
from openapi_core.schema.security_requirements.generators import (
    SecurityRequirementsGenerator,
)
from openapi_core.schema.servers.generators import ServersGenerator


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
            summary = operation_deref.get('summary')
            description = operation_deref.get('description')
            servers_spec = operation_deref.get('servers', [])

            servers = self.servers_generator.generate(servers_spec)

            security = None
            if 'security' in operation_deref:
                security_spec = operation_deref.get('security')
                security = self.security_requirements_generator.generate(
                    security_spec)

            extensions = self.extensions_generator.generate(operation_deref)

            external_docs = None
            if 'externalDocs' in operation_deref:
                external_docs_spec = operation_deref.get('externalDocs')
                external_docs = self.external_docs_factory.create(
                    external_docs_spec)

            request_body = None
            if 'requestBody' in operation_deref:
                request_body_spec = operation_deref.get('requestBody')
                request_body = self.request_body_factory.create(
                    request_body_spec)

            yield (
                http_method,
                Operation(
                    http_method, path_name, responses, list(parameters),
                    summary=summary, description=description,
                    external_docs=external_docs, security=security,
                    request_body=request_body, deprecated=deprecated,
                    operation_id=operation_id, tags=list(tags_list),
                    servers=list(servers), extensions=extensions,
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
    def external_docs_factory(self):
        return ExternalDocumentationFactory(self.dereferencer)

    @property
    @lru_cache()
    def request_body_factory(self):
        return RequestBodyFactory(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def security_requirements_generator(self):
        return SecurityRequirementsGenerator(self.dereferencer)

    @property
    @lru_cache()
    def servers_generator(self):
        return ServersGenerator(self.dereferencer)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
