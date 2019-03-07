from base64 import b64encode
import json
import pytest
from six import text_type

from openapi_core.schema.media_types.exceptions import (
    InvalidContentType, InvalidMediaTypeValue,
)
from openapi_core.extensions.models.models import BaseModel
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.parameters.exceptions import MissingRequiredParameter
from openapi_core.schema.request_bodies.exceptions import MissingRequestBody
from openapi_core.schema.responses.exceptions import (
    MissingResponseContent, InvalidResponse,
)
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.wrappers.mock import MockRequest, MockResponse


class TestRequestValidator(object):

    host_url = 'http://petstore.swagger.io'

    api_key = '12345'

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode('utf8')
        api_key_bytes_enc = b64encode(api_key_bytes)
        return text_type(api_key_bytes_enc, 'utf8')

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
        request = MockRequest('http://petstore.invalid.net/v1', 'get', '/')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidServer
        assert result.body is None
        assert result.parameters == {}

    def test_invalid_operation(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidOperation
        assert result.body is None
        assert result.parameters == {}

    def test_missing_parameter(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')

        result = validator.validate(request)

        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == {
            'query': {
                'page': 1,
                'search': '',
            },
        }

    def test_get_pets(self, validator):
        request = MockRequest(
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
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }
        request = MockRequest(
            self.host_url, 'post', '/v1/pets',
            path_pattern='/v1/pets',
            headers=headers, cookies=cookies,
        )

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequestBody
        assert result.body is None
        assert result.parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

    def test_invalid_content_type(self, validator):
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }
        request = MockRequest(
            self.host_url, 'post', '/v1/pets',
            path_pattern='/v1/pets', mimetype='text/csv',
            headers=headers, cookies=cookies,
        )

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidContentType
        assert result.body is None
        assert result.parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

    def test_post_pets(self, validator, spec_dict):
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_street = 'Piekna'
        pet_city = 'Warsaw'
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'position': 2,
            'address': {
                'street': pet_street,
                'city': pet_city,
            },
            'ears': {
                'healthy': True,
            }
        }
        data = json.dumps(data_json)
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }
        request = MockRequest(
            self.host_url, 'post', '/v1/pets',
            path_pattern='/v1/pets', data=data,
            headers=headers, cookies=cookies,
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

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
        request = MockRequest(
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


class TestResponseValidator(object):

    host_url = 'http://petstore.swagger.io'

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    @pytest.fixture
    def validator(self, spec):
        return ResponseValidator(spec)

    def test_invalid_server(self, validator):
        request = MockRequest('http://petstore.invalid.net/v1', 'get', '/')
        response = MockResponse('Not Found', status_code=404)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidServer
        assert result.data is None
        assert result.headers is None

    def test_invalid_operation(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1')
        response = MockResponse('Not Found', status_code=404)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidOperation
        assert result.data is None
        assert result.headers is None

    def test_invalid_response(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse('Not Found', status_code=409)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidResponse
        assert result.data is None
        assert result.headers is None

    def test_invalid_content_type(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse('Not Found', mimetype='text/csv')

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidContentType
        assert result.data is None
        assert result.headers == {}

    def test_missing_body(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse(None)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingResponseContent
        assert result.data is None
        assert result.headers == {}

    def test_invalid_media_type_value(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse("{}")

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidMediaTypeValue
        assert result.data is None
        assert result.headers == {}

    def test_invalid_value(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/tags')
        response_json = {
            'data': [
                {
                    'id': 1,
                    'name': 'Sparky'
                },
            ],
        }
        response_data = json.dumps(response_json)
        response = MockResponse(response_data)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidMediaTypeValue
        assert result.data is None
        assert result.headers == {}

    def test_get_pets(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response_json = {
            'data': [
                {
                    'id': 1,
                    'name': 'Sparky'
                },
            ],
        }
        response_data = json.dumps(response_json)
        response = MockResponse(response_data)

        result = validator.validate(request, response)

        assert result.errors == []
        assert isinstance(result.data, BaseModel)
        assert len(result.data.data) == 1
        assert result.data.data[0].id == 1
        assert result.data.data[0].name == 'Sparky'
        assert result.headers == {}
