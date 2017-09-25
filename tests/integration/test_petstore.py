import json
import pytest
from six import iteritems

from openapi_core.exceptions import (
    MissingParameterError, InvalidContentTypeError, InvalidServerError,
)
from openapi_core.media_types import MediaType
from openapi_core.operations import Operation
from openapi_core.paths import Path
from openapi_core.request_bodies import RequestBody
from openapi_core.schemas import Schema
from openapi_core.servers import Server, ServerVariable
from openapi_core.shortcuts import create_spec
from openapi_core.wrappers import BaseOpenAPIRequest


class RequestMock(BaseOpenAPIRequest):

    def __init__(
            self, host_url, method, path, path_pattern=None, args=None,
            view_args=None, headers=None, cookies=None, data=None,
            content_type='application/json'):
        self.host_url = host_url
        self.path = path
        self.path_pattern = path_pattern or path
        self.method = method

        self.args = args or {}
        self.view_args = view_args or {}
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.data = data or ''

        self.content_type = content_type


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
                request_body_spec = operation_spec.get('requestBody')

                assert bool(request_body_spec) == bool(operation.request_body)

                if not request_body_spec:
                    continue

                assert type(operation.request_body) == RequestBody
                assert bool(operation.request_body.required) ==\
                    request_body_spec.get('required', False)

                for content_type, media_type in iteritems(
                        operation.request_body.content):
                    assert type(media_type) == MediaType
                    assert media_type.content_type == content_type

                    content_spec = request_body_spec['content'][content_type]
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

        request = RequestMock(
            host_url, 'get', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'query': {
                'limit': 20,
                'ids': [12, 13],
            }
        }

    def test_get_pets_raises_missing_required_param(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        request = RequestMock(
            host_url, 'get', '/pets',
            path_pattern=path_pattern,
        )

        with pytest.raises(MissingParameterError):
            request.get_parameters(spec)

    def test_get_pets_failed_to_cast(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': 'non_integer_value',
        }

        request = RequestMock(
            host_url, 'get', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'query': {
                'limit': 'non_integer_value',
            }
        }

    def test_get_pets_empty_value(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': '',
        }

        request = RequestMock(
            host_url, 'get', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'query': {
                'limit': None,
            }
        }

    def test_get_pets_none_value(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': None,
        }

        request = RequestMock(
            host_url, 'get', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'query': {
                'limit': None,
            }
        }

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
            'address': {
                'street': pet_street,
                'city': pet_city,
            }
        }
        data = json.dumps(data_json)

        request = RequestMock(
            host_url, 'post', '/pets',
            path_pattern=path_pattern, data=data,
        )

        pet = request.get_body(spec)

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        address_model = schemas['Address']['x-model']
        assert pet.__class__.__name__ == pet_model
        assert pet.name == pet_name
        assert pet.tag == pet_tag
        assert pet.address.__class__.__name__ == address_model
        assert pet.address.street == pet_street
        assert pet.address.city == pet_city

    def test_post_pets_raises_invalid_content_type(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {
            'name': 'Cat',
            'tag': 'cats',
        }
        data = json.dumps(data_json)

        request = RequestMock(
            host_url, 'post', '/pets',
            path_pattern=path_pattern, data=data, content_type='text/html',
        )

        with pytest.raises(InvalidContentTypeError):
            request.get_body(spec)

    def test_post_pets_raises_invalid_server_error(self, spec):
        host_url = 'http://flowerstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {
            'name': 'Cat',
            'tag': 'cats',
        }
        data = json.dumps(data_json)

        request = RequestMock(
            host_url, 'post', '/pets',
            path_pattern=path_pattern, data=data, content_type='text/html',
        )

        with pytest.raises(InvalidServerError):
            request.get_body(spec)

    def test_get_pet(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets/{petId}'
        view_args = {
            'petId': '1',
        }
        request = RequestMock(
            host_url, 'get', '/pets/1',
            path_pattern=path_pattern, view_args=view_args,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {
            'path': {
                'petId': 1,
            }
        }
