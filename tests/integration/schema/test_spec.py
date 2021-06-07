from __future__ import division
import pytest
from base64 import b64encode

from openapi_core.shortcuts import create_spec
from openapi_core.schema.servers import get_server_url
from openapi_core.schema.specs import get_spec_url
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestPetstore:

    api_key = '12345'

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode('utf8')
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, 'utf8')

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

        info = spec / 'info'
        info_spec = spec_dict['info']
        assert info['title'] == info_spec['title']
        assert info['description'] == info_spec['description']
        assert info['termsOfService'] == info_spec['termsOfService']
        assert info['version'] == info_spec['version']

        contact = info / 'contact'
        contact_spec = info_spec['contact']
        assert contact['name'] == contact_spec['name']
        assert contact['url'] == contact_spec['url']
        assert contact['email'] == contact_spec['email']

        license = info / 'license'
        license_spec = info_spec['license']
        assert license['name'] == license_spec['name']
        assert license['url'] == license_spec['url']

        security = spec / 'security'
        security_spec = spec_dict.get('security', [])
        for idx, security_reqs in enumerate(security):
            security_reqs_spec = security_spec[idx]
            for scheme_name, security_req in security_reqs.items():
                security_req == security_reqs_spec[scheme_name]

        assert get_spec_url(spec) == url

        servers = spec / 'servers'
        for idx, server in enumerate(servers):
            server_spec = spec_dict['servers'][idx]
            assert server['url'] == server_spec['url']
            assert get_server_url(server) == url

            variables = server / 'variables'
            for variable_name, variable in variables.items():
                variable_spec = server_spec['variables'][variable_name]
                assert variable['default'] == variable_spec['default']
                assert variable['enum'] == variable_spec.get('enum')

        paths = spec / 'paths'
        for path_name, path in paths.items():
            path_spec = spec_dict['paths'][path_name]
            assert path.getkey('summary') == path_spec.get('summary')
            assert path.getkey('description') == path_spec.get('description')

            servers = path.get('servers', [])
            servers_spec = path_spec.get('servers', [])
            for idx, server in enumerate(servers):
                server_spec = servers_spec[idx]
                assert server.url == server_spec['url']
                assert server.default_url == server_spec['url']
                assert server.description == server_spec.get('description')

                variables = server.get('variables', {})
                for variable_name, variable in variables.items():
                    variable_spec = server_spec['variables'][variable_name]
                    assert variable['default'] == variable_spec['default']
                    assert variable.getkey('enum') == variable_spec.get('enum')

            operations = [
                'get', 'put', 'post', 'delete', 'options',
                'head', 'patch', 'trace',
            ]
            for http_method in operations:
                if http_method not in path:
                    continue
                operation = path / http_method
                operation_spec = path_spec[http_method]

                assert operation['operationId'] is not None
                assert operation['tags'] == operation_spec['tags']
                assert operation['summary'] == operation_spec.get('summary')
                assert operation.getkey('description') == operation_spec.get(
                    'description')

                ext_docs = operation.get('externalDocs')
                ext_docs_spec = operation_spec.get('externalDocs')
                assert bool(ext_docs_spec) == bool(ext_docs)
                if ext_docs_spec:
                    assert ext_docs['url'] == ext_docs_spec['url']
                    assert ext_docs.getkey('description') == ext_docs_spec.get(
                        'description')

                servers = operation.get('servers', [])
                servers_spec = operation_spec.get('servers', [])
                for idx, server in enumerate(servers):
                    server_spec = servers_spec[idx]
                    assert server['url'] == server_spec['url']
                    assert get_server_url(server) == server_spec['url']
                    assert server['description'] == server_spec.get(
                        'description')

                    variables = server.get('variables', {})
                    for variable_name, variable in variables.items():
                        variable_spec = server_spec['variables'][variable_name]
                        assert variable['default'] == variable_spec['default']
                        assert variable.getkey('enum') == variable_spec.get(
                            'enum')

                security = operation.get('security', [])
                security_spec = operation_spec.get('security')
                if security_spec is not None:
                    for idx, security_reqs in enumerate(security):
                        security_reqs_spec = security_spec[idx]
                        for scheme_name, security_req in security_reqs.items():
                            security_req == security_reqs_spec[scheme_name]

                responses = operation / 'responses'
                responses_spec = operation_spec.get('responses')
                for http_status, response in responses.items():
                    response_spec = responses_spec[http_status]

                    if not response_spec:
                        continue

                    # @todo: test with defererence
                    if '$ref' in response_spec:
                        continue

                    description_spec = response_spec['description']

                    assert response.getkey('description') == description_spec

                    headers = response.get('headers', {})
                    for parameter_name, parameter in headers.items():
                        headers_spec = response_spec['headers']
                        parameter_spec = headers_spec[parameter_name]

                        schema = parameter.get('schema')
                        schema_spec = parameter_spec.get('schema')
                        assert bool(schema_spec) == bool(schema)

                        if not schema_spec:
                            continue

                        # @todo: test with defererence
                        if '$ref' in schema_spec:
                            continue

                        assert schema['type'] ==\
                            schema_spec['type']
                        assert schema.getkey('format') ==\
                            schema_spec.get('format')
                        assert schema.getkey('required') == schema_spec.get(
                            'required')

                        content = parameter.get('content', {})
                        content_spec = parameter_spec.get('content')
                        assert bool(content_spec) == bool(content)

                        if not content_spec:
                            continue

                        for mimetype, media_type in content.items():
                            media_spec = parameter_spec['content'][mimetype]
                            schema = media_type.get('schema')
                            schema_spec = media_spec.get('schema')
                            assert bool(schema_spec) == bool(schema)

                            if not schema_spec:
                                continue

                            # @todo: test with defererence
                            if '$ref' in schema_spec:
                                continue

                            assert schema['type'] ==\
                                schema_spec['type']
                            assert schema.getkey('format') ==\
                                schema_spec.get('format')
                            assert schema.getkey('required') == \
                                schema_spec.get('required')

                    content_spec = response_spec.get('content')

                    if not content_spec:
                        continue

                    content = response.get('content', {})
                    for mimetype, media_type in content.items():
                        content_spec = response_spec['content'][mimetype]

                        example_spec = content_spec.get('example')
                        assert media_type.getkey('example') == example_spec

                        schema = media_type.get('schema')
                        schema_spec = content_spec.get('schema')
                        assert bool(schema_spec) == bool(schema)

                        if not schema_spec:
                            continue

                        # @todo: test with defererence
                        if '$ref' in schema_spec:
                            continue

                        assert schema['type'] == schema_spec['type']
                        assert schema.getkey('required') == schema_spec.get(
                            'required')

                request_body = operation.get('requestBody')
                request_body_spec = operation_spec.get('requestBody')
                assert bool(request_body_spec) == bool(request_body)

                if not request_body_spec:
                    continue

                assert bool(request_body.getkey('required')) ==\
                    request_body_spec.get('required')

                content = request_body / 'content'
                for mimetype, media_type in content.items():
                    content_spec = request_body_spec['content'][mimetype]
                    schema_spec = content_spec.get('schema')

                    if not schema_spec:
                        continue

                    # @todo: test with defererence
                    if '$ref' in schema_spec:
                        continue

                    schema = content.get('schema')
                    assert bool(schema_spec) == bool(schema)

                    assert schema.type.value ==\
                        schema_spec['type']
                    assert schema.format ==\
                        schema_spec.get('format')
                    assert schema.required == schema_spec.get(
                        'required', False)

        components = spec.get('components')
        if not components:
            return

        schemas = components.get('schemas', {})
        for schema_name, schema in schemas.items():
            schema_spec = spec_dict['components']['schemas'][schema_name]
            assert schema.getkey('readOnly') == schema_spec.get('readOnly')
            assert schema.getkey('writeOnly') == schema_spec.get('writeOnly')
