from base64 import b64encode
import json
import pytest
from six import text_type

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.extensions.models.models import BaseModel
from openapi_core.exceptions import (
    MissingRequiredParameter, MissingRequiredRequestBody,
    MissingResponseContent,
)
from openapi_core.shortcuts import create_spec
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import (
    PathNotFound, OperationNotFound,
)
from openapi_core.templating.responses.exceptions import ResponseNotFound
from openapi_core.testing import MockRequest, MockResponse
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.request.datatypes import RequestParameters
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestRequestValidator(object):

    host_url = 'http://petstore.swagger.io'

    api_key = '12345'

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode('utf8')
        api_key_bytes_enc = b64encode(api_key_bytes)
        return text_type(api_key_bytes_enc, 'utf8')

    @pytest.fixture(scope='session')
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture(scope='session')
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    @pytest.fixture(scope='session')
    def validator(self, spec):
        return RequestValidator(spec, base_url=self.host_url)

    def test_request_server_error(self, validator):
        request = MockRequest('http://petstore.invalid.net/v1', 'get', '/')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.body is None
        assert result.parameters == RequestParameters()

    def test_invalid_path(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.body is None
        assert result.parameters == RequestParameters()

    def test_invalid_operation(self, validator):
        request = MockRequest(self.host_url, 'patch', '/v1/pets')

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == OperationNotFound
        assert result.body is None
        assert result.parameters == RequestParameters()

    def test_missing_parameter(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')

        result = validator.validate(request)

        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == RequestParameters(
            query={
                'page': 1,
                'search': '',
            },
        )

    def test_get_pets(self, validator):
        args = {'limit': '10', 'ids': ['1', '2'], 'api_key': self.api_key}
        request = MockRequest(
            self.host_url, 'get', '/v1/pets',
            path_pattern='/v1/pets', args=args,
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == RequestParameters(
            query={
                'limit': 10,
                'page': 1,
                'search': '',
                'ids': [1, 2],
            },
        )
        assert result.security == {
            'api_key': self.api_key,
        }

    def test_get_pets_webob(self, validator):
        from webob.multidict import GetDict
        request = MockRequest(
            self.host_url, 'get', '/v1/pets',
            path_pattern='/v1/pets',
        )
        request.parameters.query = GetDict(
            [('limit', '5'), ('ids', '1'), ('ids', '2')],
            {}
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == RequestParameters(
            query={
                'limit': 5,
                'page': 1,
                'search': '',
                'ids': [1, 2],
            },
        )

    def test_missing_body(self, validator):
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }
        request = MockRequest(
            'https://development.gigantic-server.com', 'post', '/v1/pets',
            path_pattern='/v1/pets',
            headers=headers, cookies=cookies,
        )

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredRequestBody
        assert result.body is None
        assert result.parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

    def test_invalid_content_type(self, validator):
        data = "csv,data"
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }
        request = MockRequest(
            'https://development.gigantic-server.com', 'post', '/v1/pets',
            path_pattern='/v1/pets', mimetype='text/csv', data=data,
            headers=headers, cookies=cookies,
        )

        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MediaTypeNotFound
        assert result.body is None
        assert result.parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

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
            'https://development.gigantic-server.com', 'post', '/v1/pets',
            path_pattern='/v1/pets', data=data,
            headers=headers, cookies=cookies,
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )
        assert result.security == {}

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

    def test_get_pet_unauthorized(self, validator):
        request = MockRequest(
            self.host_url, 'get', '/v1/pets/1',
            path_pattern='/v1/pets/{petId}', view_args={'petId': '1'},
        )

        result = validator.validate(request)

        assert result.errors == [InvalidSecurity(), ]
        assert result.body is None
        assert result.parameters == RequestParameters()
        assert result.security is None

    def test_get_pet(self, validator):
        authorization = 'Basic ' + self.api_key_encoded
        headers = {
            'Authorization': authorization,
        }
        request = MockRequest(
            self.host_url, 'get', '/v1/pets/1',
            path_pattern='/v1/pets/{petId}', view_args={'petId': '1'},
            headers=headers,
        )

        result = validator.validate(request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == RequestParameters(
            path={
                'petId': 1,
            },
        )
        assert result.security == {
            'petstore_auth': self.api_key_encoded,
        }


class TestPathItemParamsValidator(object):

    @pytest.fixture(scope='session')
    def spec_dict(self):
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test path item parameter validation",
                "version": "0.1",
            },
            "paths": {
                "/resource": {
                    "parameters": [
                        {
                            "name": "resId",
                            "in": "query",
                            "required": True,
                            "schema": {
                                "type": "integer",
                            },
                        },
                    ],
                    "get": {
                        "responses": {
                            "default": {
                                "description": "Return the resource."
                            }
                        }
                    }
                }
            }
        }

    @pytest.fixture(scope='session')
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    @pytest.fixture(scope='session')
    def validator(self, spec):
        return RequestValidator(spec, base_url='http://example.com')

    def test_request_missing_param(self, validator):
        request = MockRequest('http://example.com', 'get', '/resource')
        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == RequestParameters()

    def test_request_invalid_param(self, validator):
        request = MockRequest(
            'http://example.com', 'get', '/resource',
            args={'resId': 'invalid'},
        )
        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == CastError
        assert result.body is None
        assert result.parameters == RequestParameters()

    def test_request_valid_param(self, validator):
        request = MockRequest(
            'http://example.com', 'get', '/resource',
            args={'resId': '10'},
        )
        result = validator.validate(request)

        assert len(result.errors) == 0
        assert result.body is None
        assert result.parameters == RequestParameters(query={'resId': 10})

    def test_request_override_param(self, spec_dict):
        # override path parameter on operation
        spec_dict["paths"]["/resource"]["get"]["parameters"] = [
            {
                # full valid parameter object required
                "name": "resId",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                },
            }
        ]
        validator = RequestValidator(
            create_spec(spec_dict), base_url='http://example.com')
        request = MockRequest('http://example.com', 'get', '/resource')
        result = validator.validate(request)

        assert len(result.errors) == 0
        assert result.body is None
        assert result.parameters == RequestParameters()

    def test_request_override_param_uniqueness(self, spec_dict):
        # add parameter on operation with same name as on path but
        # different location
        spec_dict["paths"]["/resource"]["get"]["parameters"] = [
            {
                # full valid parameter object required
                "name": "resId",
                "in": "header",
                "required": False,
                "schema": {
                    "type": "integer",
                },
            }
        ]
        validator = RequestValidator(
            create_spec(spec_dict), base_url='http://example.com')
        request = MockRequest('http://example.com', 'get', '/resource')
        result = validator.validate(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == RequestParameters()


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
        return ResponseValidator(spec, base_url=self.host_url)

    def test_invalid_server(self, validator):
        request = MockRequest('http://petstore.invalid.net/v1', 'get', '/')
        response = MockResponse('Not Found', status_code=404)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_operation(self, validator):
        request = MockRequest(self.host_url, 'patch', '/v1/pets')
        response = MockResponse('Not Found', status_code=404)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == OperationNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_response(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse('Not Found', status_code=409)

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == ResponseNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_content_type(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse('Not Found', mimetype='text/csv')

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MediaTypeNotFound
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

    def test_invalid_media_type(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse("abcde")

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == DeserializeError
        assert result.data is None
        assert result.headers == {}

    def test_invalid_media_type_value(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response = MockResponse("{}")

        result = validator.validate(request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidSchemaValue
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
        assert type(result.errors[0]) == InvalidSchemaValue
        assert result.data is None
        assert result.headers == {}

    def test_get_pets(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response_json = {
            'data': [
                {
                    'id': 1,
                    'name': 'Sparky',
                    'ears': {
                        'healthy': True,
                    },
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
