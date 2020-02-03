import json
import pytest
from datetime import datetime
from base64 import b64encode
from uuid import UUID
from six import text_type

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.parameters.exceptions import (
    EmptyParameterValue,
)
from openapi_core.extensions.models.models import BaseModel
from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.schema.parameters.exceptions import (
    MissingRequiredParameter,
)
from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.shortcuts import (
    create_spec, validate_parameters, validate_body,
)
from openapi_core.testing import MockRequest, MockResponse
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.request.datatypes import RequestParameters
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

    def test_get_pets(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': '20',
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters(
            query={
                'limit': 20,
                'page': 1,
                'search': '',
            }
        )
        assert body is None

        data_json = {
            'data': [],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.data == []

    def test_get_pets_response(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': '20',
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters(
            query={
                'limit': 20,
                'page': 1,
                'search': '',
            }
        )
        assert body is None

        data_json = {
            'data': [
                {
                    'id': 1,
                    'name': 'Cat',
                    'ears': {
                        'healthy': True,
                    },
                }
            ],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert len(response_result.data.data) == 1
        assert response_result.data.data[0].id == 1
        assert response_result.data.data[0].name == 'Cat'

    def test_get_pets_invalid_response(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': '20',
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters(
            query={
                'limit': 20,
                'page': 1,
                'search': '',
            }
        )
        assert body is None

        data_json = {
            'data': [
                {
                    'id': 1,
                    'name': {
                        'first_name': 'Cat',
                    },
                }
            ],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        schema_errors = response_result.errors[0].schema_errors
        assert response_result.errors == [
            InvalidSchemaValue(
                type=SchemaType.OBJECT,
                value=data_json,
                schema_errors=schema_errors,
            ),
        ]
        assert response_result.data is None

    def test_get_pets_ids_param(self, spec, response_validator):
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

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters(
            query={
                'limit': 20,
                'page': 1,
                'search': '',
                'ids': [12, 13],
            }
        )
        assert body is None

        data_json = {
            'data': [],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.data == []

    def test_get_pets_tags_param(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = [
            ('limit', '20'),
            ('tags', 'cats,dogs'),
        ]

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters(
            query={
                'limit': 20,
                'page': 1,
                'search': '',
                'tags': ['cats', 'dogs'],
            }
        )
        assert body is None

        data_json = {
            'data': [],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.data == []

    def test_get_pets_parameter_deserialization_error(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        query_params = {
            'limit': 1,
            'tags': 12,
        }

        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern, args=query_params,
        )

        with pytest.raises(DeserializeError):
            validate_parameters(spec, request)

        body = validate_body(spec, request)

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

        with pytest.raises(CastError):
            validate_parameters(spec, request)

        body = validate_body(spec, request)

        assert body is None

    def test_get_pets_raises_missing_required_param(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        request = MockRequest(
            host_url, 'GET', '/pets',
            path_pattern=path_pattern,
        )

        with pytest.raises(MissingRequiredParameter):
            validate_parameters(spec, request)

        body = validate_body(spec, request)

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

        with pytest.raises(EmptyParameterValue):
            validate_parameters(spec, request)
        body = validate_body(spec, request)

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

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            query={
                'limit': None,
                'page': 1,
                'search': '',
            }
        )

        body = validate_body(spec, request)

        assert body is None

    def test_post_birds(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_street = 'Piekna'
        pet_city = 'Warsaw'
        pet_healthy = False
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'position': 2,
            'address': {
                'street': pet_street,
                'city': pet_city,
            },
            'healthy': pet_healthy,
            'wings': {
                'healthy': pet_healthy,
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
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            headers=headers, cookies=cookies,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

        body = validate_body(spec, request)

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
        assert body.healthy == pet_healthy

    def test_post_cats(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_street = 'Piekna'
        pet_city = 'Warsaw'
        pet_healthy = False
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'position': 2,
            'address': {
                'street': pet_street,
                'city': pet_city,
            },
            'healthy': pet_healthy,
            'ears': {
                'healthy': pet_healthy,
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
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            headers=headers, cookies=cookies,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

        body = validate_body(spec, request)

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
        assert body.healthy == pet_healthy

    def test_post_cats_boolean_string(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_tag = 'cats'
        pet_street = 'Piekna'
        pet_city = 'Warsaw'
        pet_healthy = False
        data_json = {
            'name': pet_name,
            'tag': pet_tag,
            'position': 2,
            'address': {
                'street': pet_street,
                'city': pet_city,
            },
            'healthy': pet_healthy,
            'ears': {
                'healthy': pet_healthy,
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
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            headers=headers, cookies=cookies,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

        body = validate_body(spec, request)

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
        assert body.healthy is False

    def test_post_no_one_of_schema(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        alias = 'kitty'
        data_json = {
            'name': pet_name,
            'alias': alias,
        }
        data = json.dumps(data_json)
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            headers=headers, cookies=cookies,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

        with pytest.raises(InvalidSchemaValue):
            validate_body(spec, request)

    def test_post_cats_only_required_body(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_healthy = True
        data_json = {
            'name': pet_name,
            'ears': {
                'healthy': pet_healthy,
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
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            headers=headers, cookies=cookies,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

        body = validate_body(spec, request)

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        assert body.__class__.__name__ == pet_model
        assert body.name == pet_name
        assert not hasattr(body, 'tag')
        assert not hasattr(body, 'address')

    def test_post_pets_raises_invalid_mimetype(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {
            'name': 'Cat',
            'tag': 'cats',
        }
        data = json.dumps(data_json)
        headers = {
            'api_key': self.api_key_encoded,
        }
        cookies = {
            'user': '123',
        }

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data, mimetype='text/html',
            headers=headers, cookies=cookies,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            header={
                'api_key': self.api_key,
            },
            cookie={
                'user': 123,
            },
        )

        with pytest.raises(InvalidContentType):
            validate_body(spec, request)

    def test_post_pets_missing_cookie(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_healthy = True
        data_json = {
            'name': pet_name,
            'ears': {
                'healthy': pet_healthy,
            }
        }
        data = json.dumps(data_json)
        headers = {
            'api_key': self.api_key_encoded,
        }

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            headers=headers,
        )

        with pytest.raises(MissingRequiredParameter):
            validate_parameters(spec, request)

        body = validate_body(spec, request)

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        assert body.__class__.__name__ == pet_model
        assert body.name == pet_name
        assert not hasattr(body, 'tag')
        assert not hasattr(body, 'address')

    def test_post_pets_missing_header(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        pet_name = 'Cat'
        pet_healthy = True
        data_json = {
            'name': pet_name,
            'ears': {
                'healthy': pet_healthy,
            }
        }
        data = json.dumps(data_json)
        cookies = {
            'user': '123',
        }

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data,
            cookies=cookies,
        )

        with pytest.raises(MissingRequiredParameter):
            validate_parameters(spec, request)

        body = validate_body(spec, request)

        schemas = spec_dict['components']['schemas']
        pet_model = schemas['PetCreate']['x-model']
        assert body.__class__.__name__ == pet_model
        assert body.name == pet_name
        assert not hasattr(body, 'tag')
        assert not hasattr(body, 'address')

    def test_post_pets_raises_invalid_server_error(self, spec):
        host_url = 'http://flowerstore.swagger.io/v1'
        path_pattern = '/v1/pets'
        data_json = {
            'name': 'Cat',
            'tag': 'cats',
        }
        data = json.dumps(data_json)
        headers = {
            'api_key': '12345',
        }
        cookies = {
            'user': '123',
        }

        request = MockRequest(
            host_url, 'POST', '/pets',
            path_pattern=path_pattern, data=data, mimetype='text/html',
            headers=headers, cookies=cookies,
        )

        with pytest.raises(InvalidServer):
            validate_parameters(spec, request)

        with pytest.raises(InvalidServer):
            validate_body(spec, request)

    def test_get_pet(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets/{petId}'
        view_args = {
            'petId': '1',
        }
        request = MockRequest(
            host_url, 'GET', '/pets/1',
            path_pattern=path_pattern, view_args=view_args,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            path={
                'petId': 1,
            }
        )

        body = validate_body(spec, request)

        assert body is None

        data_id = 1
        data_name = 'test'
        data_json = {
            'data': {
                'id': data_id,
                'name': data_name,
                'ears': {
                    'healthy': True,
                },
            },
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert isinstance(response_result.data.data, BaseModel)
        assert response_result.data.data.id == data_id
        assert response_result.data.data.name == data_name

    def test_get_pet_not_found(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets/{petId}'
        view_args = {
            'petId': '1',
        }
        request = MockRequest(
            host_url, 'GET', '/pets/1',
            path_pattern=path_pattern, view_args=view_args,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            path={
                'petId': 1,
            }
        )

        body = validate_body(spec, request)

        assert body is None

        code = 404
        message = 'Not found'
        rootCause = 'Pet not found'
        data_json = {
            'code': 404,
            'message': message,
            'rootCause': rootCause,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause

    def test_get_pet_wildcard(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/pets/{petId}'
        view_args = {
            'petId': '1',
        }
        request = MockRequest(
            host_url, 'GET', '/pets/1',
            path_pattern=path_pattern, view_args=view_args,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters(
            path={
                'petId': 1,
            }
        )

        body = validate_body(spec, request)

        assert body is None

        data = b'imagedata'
        response = MockResponse(data, mimetype='image/png')

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert response_result.data == data

    def test_get_tags(self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'

        request = MockRequest(
            host_url, 'GET', '/tags',
            path_pattern=path_pattern,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters()
        assert body is None

        data_json = ['cats', 'birds']
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert response_result.data == data_json

    def test_post_tags_extra_body_properties(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        pet_name = 'Dog'
        alias = 'kitty'
        data_json = {
            'name': pet_name,
            'alias': alias,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters()

        with pytest.raises(InvalidSchemaValue):
            validate_body(spec, request)

    def test_post_tags_empty_body(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        data_json = {}
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters()

        with pytest.raises(InvalidSchemaValue):
            validate_body(spec, request)

    def test_post_tags_wrong_property_type(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        tag_name = 123
        data = json.dumps(tag_name)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)

        assert parameters == RequestParameters()

        with pytest.raises(InvalidSchemaValue):
            validate_body(spec, request)

    def test_post_tags_additional_properties(
            self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        pet_name = 'Dog'
        data_json = {
            'name': pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters()
        assert isinstance(body, BaseModel)
        assert body.name == pet_name

        code = 400
        message = 'Bad request'
        rootCause = 'Tag already exist'
        additionalinfo = 'Tag Dog already exist'
        data_json = {
            'code': code,
            'message': message,
            'rootCause': rootCause,
            'additionalinfo': additionalinfo,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_created_now(
            self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        created = 'now'
        pet_name = 'Dog'
        data_json = {
            'created': created,
            'name': pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters()
        assert isinstance(body, BaseModel)
        assert body.created == created
        assert body.name == pet_name

        code = 400
        message = 'Bad request'
        rootCause = 'Tag already exist'
        additionalinfo = 'Tag Dog already exist'
        data_json = {
            'code': 400,
            'message': 'Bad request',
            'rootCause': 'Tag already exist',
            'additionalinfo': 'Tag Dog already exist',
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_created_datetime(
            self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        created = '2016-04-16T16:06:05Z'
        pet_name = 'Dog'
        data_json = {
            'created': created,
            'name': pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)
        body = validate_body(spec, request)

        assert parameters == RequestParameters()
        assert isinstance(body, BaseModel)
        assert body.created == datetime(2016, 4, 16, 16, 6, 5)
        assert body.name == pet_name

        code = 400
        message = 'Bad request'
        rootCause = 'Tag already exist'
        additionalinfo = 'Tag Dog already exist'
        data_json = {
            'code': code,
            'message': message,
            'rootCause': rootCause,
            'additionalinfo': additionalinfo,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_created_invalid_type(
            self, spec, response_validator):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        created = 'long time ago'
        pet_name = 'Dog'
        data_json = {
            'created': created,
            'name': pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = validate_parameters(spec, request)
        with pytest.raises(InvalidSchemaValue):
            validate_body(spec, request)

        assert parameters == RequestParameters()

        code = 400
        message = 'Bad request'
        correlationId = UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')
        rootCause = 'Tag already exist'
        additionalinfo = 'Tag Dog already exist'
        data_json = {
            'code': code,
            'message': message,
            'correlationId': str(correlationId),
            'rootCause': rootCause,
            'additionalinfo': additionalinfo,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = response_validator.validate(request, response)

        assert response_result.errors == []
        assert isinstance(response_result.data, BaseModel)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.correlationId == correlationId
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo
