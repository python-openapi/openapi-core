import json
import pytest

from openapi_core.exceptions import (
    InvalidServerError, InvalidOperationError, MissingParameterError,
    MissingBodyError, InvalidContentTypeError,
)
from openapi_core.shortcuts import create_spec
from openapi_core.validators import RequestValidator
from openapi_core.wrappers import BaseOpenAPIRequest


class RequestMock(BaseOpenAPIRequest):

    def __init__(
            self, host_url, method, path, path_pattern=None, args=None,
            view_args=None, headers=None, cookies=None, data=None,
            mimetype='application/json'):
        self.host_url = host_url
        self.path = path
        self.path_pattern = path_pattern or path
        self.method = method

        self.args = args or {}
        self.view_args = view_args or {}
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.data = data or ''

        self.mimetype = mimetype


class TestRequestValidator(object):

    host_url = 'http://petstore.swagger.io'

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    @pytest.fixture
    def validator(self, spec):
        return RequestValidator(spec)

    def test_request_server_error(self, validator):
        request = RequestMock('http://petstore.invalid.net/v1', 'get', '/')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidServerError
        assert result.body is None
        assert result.parameters == {}

    def test_invalid_operation(self, validator):
        request = RequestMock(self.host_url, 'get', '/v1')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidOperationError
        assert result.body is None
        assert result.parameters == {}

    def test_missing_parameter(self, validator):
        request = RequestMock(self.host_url, 'get', '/v1/pets')

        result = validator.validate(request)

        assert type(result.errors[0]) == MissingParameterError
        assert result.body is None
        assert result.parameters == {
            'query': {
                'page': 1,
                'search': '',
            },
        }

    def test_get_pets(self, validator):
        request = RequestMock(
            self.host_url, 'get', '/v1/pets',
            path_pattern='/v1/pets', args={'limit': '10'},
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == {
            'query': {
                'limit': 10,
                'page': 1,
                'search': '',
            },
        }

    def test_missing_body(self, validator):
        request = RequestMock(
            self.host_url, 'post', '/v1/pets',
            path_pattern='/v1/pets',
        )

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingBodyError
        assert result.body is None
        assert result.parameters == {}

    def test_invalid_content_type(self, validator):
        request = RequestMock(
            self.host_url, 'post', '/v1/pets',
            path_pattern='/v1/pets', mimetype='text/csv',
        )

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidContentTypeError
        assert result.body is None
        assert result.parameters == {}

    def test_post_pets(self, validator, spec_dict):
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
        request = RequestMock(
            self.host_url, 'post', '/v1/pets',
            path_pattern='/v1/pets', data=data,
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.parameters == {}

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        address_model = schemas['Address']['x-model']
        assert result.body.__class__.__name__ == pet_model
        assert result.body.name == pet_name
        assert result.body.tag == pet_tag
        assert result.body.position == 2
        assert result.body.address.__class__.__name__ == address_model
        assert result.body.address.street == pet_street
        assert result.body.address.city == pet_city

    def test_get_pet(self, validator):
        request = RequestMock(
            self.host_url, 'get', '/v1/pets/1',
            path_pattern='/v1/pets/{petId}', view_args={'petId': '1'},
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == {
            'path': {
                'petId': 1,
            },
        }
