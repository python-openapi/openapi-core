import json
import pytest
from base64 import b64encode
from uuid import UUID
from six import iteritems, text_type

from openapi_core.extensions.models.models import BaseModel
from openapi_core.schema.media_types.exceptions import (
    InvalidContentType, InvalidMediaTypeValue,
)
from openapi_core.schema.media_types.models import MediaType
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.parameters.exceptions import (
    MissingRequiredParameter, InvalidParameterValue, EmptyParameterValue,
)
from openapi_core.schema.parameters.models import Parameter
from openapi_core.schema.paths.models import Path
from openapi_core.schema.request_bodies.models import RequestBody
from openapi_core.schema.responses.models import Response
from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.exceptions import (
    NoValidSchema, InvalidSchemaProperty, InvalidSchemaValue,
)
from openapi_core.schema.schemas.models import Schema
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.schema.servers.models import Server, ServerVariable
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.wrappers.mock import MockRequest, MockResponse


class TestPetstore(object):

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
    def request_validator(self, spec):
        return RequestValidator(spec)

    @pytest.fixture
    def response_validator(self, spec):
        return ResponseValidator(spec)

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
                operation_spec = spec_dict['paths'][path_name][http_method]

                assert type(operation) == Operation
                assert operation.path_name == path_name
                assert operation.http_method == http_method
                assert operation.operation_id is not None
                assert operation.tags == operation_spec['tags']

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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {
            'query': {
                'limit': 20,
                'page': 1,
                'search': '',
            }
        }
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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {
            'query': {
                'limit': 20,
                'page': 1,
                'search': '',
            }
        }
        assert body is None

        data_json = {
            'data': [
                {
                    'id': 1,
                    'name': 'Cat',
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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {
            'query': {
                'limit': 20,
                'page': 1,
                'search': '',
            }
        }
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

        assert response_result.errors == [
            InvalidMediaTypeValue(
                original_exception=InvalidSchemaProperty(
                    property_name='data',
                    original_exception=InvalidSchemaProperty(
                        property_name='name',
                        original_exception=InvalidSchemaValue(
                            msg="Value {value} is not of type {type}",
                            type=SchemaType.STRING,
                            value={'first_name': 'Cat'},
                        ),
                    ),
                ),
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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {
            'query': {
                'limit': 20,
                'page': 1,
                'search': '',
                'tags': ['cats', 'dogs'],
            }
        }
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

        with pytest.raises(InvalidParameterValue):
            request.get_parameters(spec)

        body = request.get_body(spec)

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

        with pytest.raises(MissingRequiredParameter):
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

        with pytest.raises(EmptyParameterValue):
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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

        with pytest.raises(InvalidMediaTypeValue):
            request.get_body(spec)

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

        body = request.get_body(spec)

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'header': {
                'api_key': self.api_key,
            },
            'cookie': {
                'user': 123,
            },
        }

        with pytest.raises(InvalidContentType):
            request.get_body(spec)

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
            request.get_parameters(spec)

        body = request.get_body(spec)

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
            request.get_parameters(spec)

        body = request.get_body(spec)

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
            request.get_parameters(spec)

        with pytest.raises(InvalidServer):
            request.get_body(spec)

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'path': {
                'petId': 1,
            }
        }

        body = request.get_body(spec)

        assert body is None

        data_id = 1
        data_name = 'test'
        data_json = {
            'data': {
                'id': data_id,
                'name': data_name,
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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'path': {
                'petId': 1,
            }
        }

        body = request.get_body(spec)

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

        parameters = request.get_parameters(spec)

        assert parameters == {
            'path': {
                'petId': 1,
            }
        }

        body = request.get_body(spec)

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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {}
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

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(InvalidMediaTypeValue):
            request.get_body(spec)

    def test_post_tags_empty_body(self, spec, spec_dict):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        data_json = {}
        data = json.dumps(data_json)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(InvalidMediaTypeValue):
            request.get_body(spec)

    def test_post_tags_wrong_property_type(self, spec):
        host_url = 'http://petstore.swagger.io/v1'
        path_pattern = '/v1/tags'
        tag_name = 123
        data = json.dumps(tag_name)

        request = MockRequest(
            host_url, 'POST', '/tags',
            path_pattern=path_pattern, data=data,
        )

        parameters = request.get_parameters(spec)

        assert parameters == {}

        with pytest.raises(InvalidMediaTypeValue):
            request.get_body(spec)

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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {}
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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {}
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

        parameters = request.get_parameters(spec)
        body = request.get_body(spec)

        assert parameters == {}
        assert isinstance(body, BaseModel)
        assert body.created == created
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

    @pytest.mark.xfail(reason='OneOf for string not supported atm')
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

        parameters = request.get_parameters(spec)
        with pytest.raises(NoValidSchema):
            request.get_body(spec)

        assert parameters == {}

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
