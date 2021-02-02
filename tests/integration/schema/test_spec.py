import pytest
from base64 import b64encode
from six import iteritems, text_type

from openapi_core.schema.media_types.models import MediaType
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.paths.models import Path
from openapi_core.schema.request_bodies.models import RequestBody
from openapi_core.schema.responses.models import Response
from openapi_core.schema.schemas.models import Schema
from openapi_core.schema.security_requirements.models import (
    SecurityRequirement,
)
from openapi_core.schema.servers.models import Server, ServerVariable
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestPetstore(object):

    api_key = '12345'

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode('utf8')
        api_key_bytes_enc = b64encode(api_key_bytes)
        return text_type(api_key_bytes_enc, 'utf8')

    @pytest.fixture
    def spec_uri(self):
        return "file://tests/integration/data/v3.0/petstore.yaml"

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture
    def spec(self, spec_dict, spec_uri):
        return create_spec(spec_dict, spec_uri)

    @pytest.fixture
    def request_validator(self, spec):
        return RequestValidator(spec)

    @pytest.fixture
    def response_validator(self, spec):
        return ResponseValidator(spec)

    def test_spec(self, spec, spec_dict):
        url = 'http://petstore.swagger.io/v1'

        info_spec = spec_dict['info']
        assert spec.info.title == info_spec['title']
        assert spec.info.description == info_spec['description']
        assert spec.info.terms_of_service == info_spec['termsOfService']
        assert spec.info.version == info_spec['version']

        contact_spec = info_spec['contact']
        assert spec.info.contact.name == contact_spec['name']
        assert spec.info.contact.url == contact_spec['url']
        assert spec.info.contact.email == contact_spec['email']

        license_spec = info_spec['license']
        assert spec.info.license.name == license_spec['name']
        assert spec.info.license.url == license_spec['url']

        security_spec = spec_dict.get('security', [])
        for idx, security_req in enumerate(spec.security):
            assert type(security_req) == SecurityRequirement

            security_req_spec = security_spec[idx]
            for scheme_name in security_req:
                security_req[scheme_name] == security_req_spec[scheme_name]

        assert spec.get_server_url() == url

        for idx, server in enumerate(spec.servers):
            assert type(server) == Server

            server_spec = spec_dict['servers'][idx]
            assert server.url == server_spec['url']
            assert server.default_url == url

            for variable_name, variable in iteritems(server.variables):
                assert type(variable) == ServerVariable
                assert variable.name == variable_name

                variable_spec = server_spec['variables'][variable_name]
                assert variable.default == variable_spec['default']
                assert variable.enum == variable_spec.get('enum')

        for path_name, path in iteritems(spec.paths):
            assert type(path) == Path

            path_spec = spec_dict['paths'][path_name]
            assert path.name == path_name
            assert path.summary == path_spec.get('summary')
            assert path.description == path_spec.get('description')

            servers_spec = path_spec.get('servers', [])
            for idx, server in enumerate(path.servers):
                assert type(server) == Server

                server_spec = servers_spec[idx]
                assert server.url == server_spec['url']
                assert server.default_url == server_spec['url']
                assert server.description == server_spec.get('description')

                for variable_name, variable in iteritems(server.variables):
                    assert type(variable) == ServerVariable
                    assert variable.name == variable_name

                    variable_spec = server_spec['variables'][variable_name]
                    assert variable.default == variable_spec['default']
                    assert variable.enum == variable_spec.get('enum')

            for http_method, operation in iteritems(path.operations):
                operation_spec = path_spec[http_method]

                assert type(operation) == Operation
                assert operation.path_name == path_name
                assert operation.http_method == http_method
                assert operation.operation_id is not None
                assert operation.tags == operation_spec['tags']
                assert operation.summary == operation_spec.get('summary')
                assert operation.description == operation_spec.get(
                    'description')

                ext_docs_spec = operation_spec.get('externalDocs')
                if ext_docs_spec:
                    ext_docs = operation.external_docs
                    assert ext_docs.url == ext_docs_spec['url']
                    assert ext_docs.description == ext_docs_spec.get(
                        'description')

                servers_spec = operation_spec.get('servers', [])
                for idx, server in enumerate(operation.servers):
                    assert type(server) == Server

                    server_spec = servers_spec[idx]
                    assert server.url == server_spec['url']
                    assert server.default_url == server_spec['url']
                    assert server.description == server_spec.get('description')

                    for variable_name, variable in iteritems(server.variables):
                        assert type(variable) == ServerVariable
                        assert variable.name == variable_name

                        variable_spec = server_spec['variables'][variable_name]
                        assert variable.default == variable_spec['default']
                        assert variable.enum == variable_spec.get('enum')

                security_spec = operation_spec.get('security')
                if security_spec is not None:
                    for idx, security_req in enumerate(operation.security):
                        assert type(security_req) == SecurityRequirement

                        security_req_spec = security_spec[idx]
                        for scheme_name in security_req:
                            security_req[scheme_name] == security_req_spec[
                                scheme_name]

                responses_spec = operation_spec.get('responses')

                for http_status, response in iteritems(operation.responses):
                    assert type(response) == Response
                    assert response.http_status == http_status

                    response_spec = responses_spec[http_status]

                    if not response_spec:
                        continue

                    # @todo: test with defererence
                    if '$ref' in response_spec:
                        continue

                    description_spec = response_spec['description']

                    assert response.description == description_spec

                    for mimetype, media_type in iteritems(response.content):
                        assert type(media_type) == MediaType
                        assert media_type.mimetype == mimetype

                        content_spec = response_spec['content'][mimetype]

                        example_spec = content_spec.get('example')
                        assert media_type.example == example_spec

                        schema_spec = content_spec.get('schema')
                        assert bool(schema_spec) == bool(media_type.schema)

                        if not schema_spec:
                            continue

                        # @todo: test with defererence
                        if '$ref' in schema_spec:
                            continue

                        assert type(media_type.schema) == Schema
                        assert media_type.schema.type.value ==\
                            schema_spec['type']
                        assert media_type.schema.required == schema_spec.get(
                            'required', [])

                    for parameter_name, parameter in iteritems(
                            response.headers):
                        assert type(parameter) == Parameter
                        assert parameter.name == parameter_name

                        headers_spec = response_spec['headers']
                        parameter_spec = headers_spec[parameter_name]
                        schema_spec = parameter_spec.get('schema')
                        assert bool(schema_spec) == bool(parameter.schema)

                        if not schema_spec:
                            continue

                        # @todo: test with defererence
                        if '$ref' in schema_spec:
                            continue

                        assert type(parameter.schema) == Schema
                        assert parameter.schema.type.value ==\
                            schema_spec['type']
                        assert parameter.schema.format ==\
                            schema_spec.get('format')
                        assert parameter.schema.required == schema_spec.get(
                            'required', [])

                request_body_spec = operation_spec.get('requestBody')

                assert bool(request_body_spec) == bool(operation.request_body)

                if not request_body_spec:
                    continue

                assert type(operation.request_body) == RequestBody
                assert bool(operation.request_body.required) ==\
                    request_body_spec.get('required', False)

                for mimetype, media_type in iteritems(
                        operation.request_body.content):
                    assert type(media_type) == MediaType
                    assert media_type.mimetype == mimetype

                    content_spec = request_body_spec['content'][mimetype]
                    schema_spec = content_spec.get('schema')
                    assert bool(schema_spec) == bool(media_type.schema)

                    if not schema_spec:
                        continue

                    # @todo: test with defererence
                    if '$ref' in schema_spec:
                        continue

                    assert type(media_type.schema) == Schema
                    assert media_type.schema.type.value ==\
                        schema_spec['type']
                    assert media_type.schema.format ==\
                        schema_spec.get('format')
                    assert media_type.schema.required == schema_spec.get(
                        'required', False)

        if not spec.components:
            return

        for schema_name, schema in iteritems(spec.components.schemas):
            assert type(schema) == Schema

            schema_spec = spec_dict['components']['schemas'][schema_name]
            assert schema.read_only == schema_spec.get('readOnly', False)
            assert schema.write_only == schema_spec.get('writeOnly', False)
