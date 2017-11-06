import json
import pytest
from six import iteritems

from openapi_core.exceptions import (
    MissingParameter, InvalidContentType, InvalidServer,
    UndefinedSchemaProperty, MissingProperty,
    EmptyValue, InvalidMediaTypeValue, InvalidParameterValue,
)
from openapi_core.media_types import MediaType
from openapi_core.operations import Operation
from openapi_core.parameters import Parameter
from openapi_core.paths import Path
from openapi_core.request_bodies import RequestBody
from openapi_core.responses import Response
from openapi_core.schemas import Schema
from openapi_core.servers import Server, ServerVariable
from openapi_core.shortcuts import create_spec
from openapi_core.wrappers import MockRequest


class TestPetstore(object):

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    def test_spec(self, spec, spec_dict):
        url = 'http://petstore.swagger.io/v1'
        assert spec.info.title == spec_dict['info']['title']
        assert spec.info.version == spec_dict['info']['version']

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
            assert path.name == path_name

            for http_method, operation in iteritems(path.operations):
                assert type(operation) == Operation
                assert operation.path_name == path_name
                assert operation.http_method == http_method

                operation_spec = spec_dict['paths'][path_name][http_method]

                responses_spec = operation_spec.get('responses')

                for http_status, response in iteritems(operation.responses):
                    assert type(response) == Response
                    assert response.http_status == http_status

                    response_spec = responses_spec[http_status]
                    description_spec = response_spec['description']

                    assert response.description == description_spec

                    for mimetype, media_type in iteritems(response.content):
                        assert type(media_type) == MediaType
                        assert media_type.mimetype == mimetype

                        content_spec = response_spec['content'][mimetype]
                        schema_spec = content_spec.get('schema')
                        assert bool(schema_spec) == bool(media_type.schema)

                        if not schema_spec:
                            continue

                        # @todo: test with defererence
                        if '$ref' in schema_spec:
                            continue

                        assert type(media_type.schema) == Schema
                        assert media_type.schema.type == schema_spec['type']
                        assert media_type.schema.required == schema_spec.get(
                            'required', False)

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
                        assert parameter.schema.type == schema_spec['type']
                        assert parameter.schema.required == schema_spec.get(
                            'required', False)

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
                    assert media_type.schema.type == schema_spec['type']
                    assert media_type.schema.required == schema_spec.get(
                        'required', False)

        if not spec.components:
            return

        for schema_name, schema in iteritems(spec.components.schemas):
            assert type(schema) == Schema

    def test_get_pets(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': '20',
            'ids': ['12', '13'],
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {
            'query': {
                'limit': 20,
                'page': 1,
                'search': '',
                'ids': [12, 13],
            }
        }
        assert body is None

    def test_get_pets_wrong_parameter_type(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': 'twenty',
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        with pytest.raises(InvalidParameterValue):
            request.get_parameters(spec)

        body = request.get_body(spec)

        assert body is None

    def test_get_pets_raises_missing_required_param(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern,
        )

        with pytest.raises(MissingParameter):
            request.get_parameters(spec)

        body = request.get_body(spec)

        assert body is None

    def test_get_pets_empty_value(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': '',
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        with pytest.raises(EmptyValue):
            request.get_parameters(spec)
        body = request.get_body(spec)

        assert body is None

    def test_get_pets_none_value(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': None,
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'query': {
                'limit': None,
                'page': 1,
                'search': '',
            }
        }

        body = request.get_body(spec)

        assert body is None

    def test_post_pets(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_street = 'Piekna'
        pet_city = 'Warsaw'
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'position': '2',
            'address': {
                'street': pet_street,
                'city': pet_city,
            }
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        body = request.get_body(spec)

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        address_model = schemas['Address']['x-model']
        assert body.__class__.__name__ == pet_model
        assert body.name == pet_name
        assert body.tag == pet_tag
        assert body.position == 2
        assert body.address.__class__.__name__ == address_model
        assert body.address.street == pet_street
        assert body.address.city == pet_city

    def test_post_pets_empty_body(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {}
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(MissingProperty):
            request.get_body(spec)

    def test_post_pets_extra_body_properties(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        alias = 'kitty'
        data_json = {
            'name': pet_name,
            'alias': alias,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(UndefinedSchemaProperty):
            request.get_body(spec)

    def test_post_pets_only_required_body(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        data_json = {
            'name': pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        body = request.get_body(spec)

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        assert body.__class__.__name__ == pet_model
        assert body.name == pet_name
        assert not hasattr(body, 'tag')
        assert not hasattr(body, 'address')

    def test_get_pets_wrong_body_type(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_address = 'address text'
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'address': pet_address,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(InvalidMediaTypeValue):
            request.get_body(spec)

    def test_post_pets_raises_invalid_mimetype(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {
            'name': 'Cat',
            'tag': 'cats',
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data, mimetype='text/html',
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(InvalidContentType):
            request.get_body(spec)

    def test_post_pets_raises_invalid_server_error(self, spec):
        host_url = 'http://flowerstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {
            'name': 'Cat',
            'tag': 'cats',
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data, mimetype='text/html',
        )

        with pytest.raises(InvalidServer):
            request.get_parameters(spec)

        with pytest.raises(InvalidServer):
            request.get_body(spec)

    def test_get_pet(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets/{petId}'
        view_args = {
            'petId': '1',
        }
        request = MockRequest(
            host_url, 'GET', '/pets/1',
            path_pattern=path_pattern, view_args=view_args,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'path': {
                'petId': 1,
            }
        }

        body = request.get_body(spec)

        assert body is None
