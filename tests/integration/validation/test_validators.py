import json
from base64 import b64encode

import pytest

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)
from openapi_core.extensions.models.models import BaseModel
from openapi_core.spec import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.responses.exceptions import ResponseNotFound
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation import openapi_request_validator
from openapi_core.validation import openapi_response_validator
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.exceptions import MissingRequiredParameter
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
)
from openapi_core.validation.response.exceptions import MissingResponseContent


class TestRequestValidator:

    host_url = "http://petstore.swagger.io"

    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    @pytest.fixture(scope="session")
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture(scope="session")
    def spec(self, spec_dict):
        return Spec.create(spec_dict)

    def test_request_server_error(self, spec):
        request = MockRequest("http://petstore.invalid.net/v1", "get", "/")

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.body is None
        assert result.parameters == Parameters()

    def test_invalid_path(self, spec):
        request = MockRequest(self.host_url, "get", "/v1")

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.body is None
        assert result.parameters == Parameters()

    def test_invalid_operation(self, spec):
        request = MockRequest(self.host_url, "patch", "/v1/pets")

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == OperationNotFound
        assert result.body is None
        assert result.parameters == Parameters()

    def test_missing_parameter(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")

        with pytest.warns(DeprecationWarning):
            result = openapi_request_validator.validate(spec, request)

        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == Parameters(
            query={
                "page": 1,
                "search": "",
            },
        )

    def test_get_pets(self, spec):
        args = {"limit": "10", "ids": ["1", "2"], "api_key": self.api_key}
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets",
            path_pattern="/v1/pets",
            args=args,
        )

        with pytest.warns(DeprecationWarning):
            result = openapi_request_validator.validate(spec, request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == Parameters(
            query={
                "limit": 10,
                "page": 1,
                "search": "",
                "ids": [1, 2],
            },
        )
        assert result.security == {
            "api_key": self.api_key,
        }

    def test_get_pets_webob(self, spec):
        from webob.multidict import GetDict

        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets",
            path_pattern="/v1/pets",
        )
        request.parameters.query = GetDict(
            [("limit", "5"), ("ids", "1"), ("ids", "2")], {}
        )

        with pytest.warns(DeprecationWarning):
            result = openapi_request_validator.validate(spec, request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == Parameters(
            query={
                "limit": 5,
                "page": 1,
                "search": "",
                "ids": [1, 2],
            },
        )

    def test_missing_body(self, spec):
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }
        request = MockRequest(
            "https://development.gigantic-server.com",
            "post",
            "/v1/pets",
            path_pattern="/v1/pets",
            headers=headers,
            cookies=cookies,
        )

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredRequestBody
        assert result.body is None
        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

    def test_invalid_content_type(self, spec):
        data = "csv,data"
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }
        request = MockRequest(
            "https://development.gigantic-server.com",
            "post",
            "/v1/pets",
            path_pattern="/v1/pets",
            mimetype="text/csv",
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MediaTypeNotFound
        assert result.body is None
        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

    def test_invalid_complex_parameter(self, spec, spec_dict):
        pet_name = "Cat"
        pet_tag = "cats"
        pet_street = "Piekna"
        pet_city = "Warsaw"
        data_json = {
            "name": pet_name,
            "tag": pet_tag,
            "position": 2,
            "address": {
                "street": pet_street,
                "city": pet_city,
            },
            "ears": {
                "healthy": True,
            },
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }
        userdata = {
            "name": 1,
        }
        userdata_json = json.dumps(userdata)
        cookies = {
            "user": "123",
            "userdata": userdata_json,
        }
        request = MockRequest(
            "https://development.gigantic-server.com",
            "post",
            "/v1/pets",
            path_pattern="/v1/pets",
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidSchemaValue
        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )
        assert result.security == {}

        schemas = spec_dict["components"]["schemas"]
        pet_model = schemas["PetCreate"]["x-model"]
        address_model = schemas["Address"]["x-model"]
        assert result.body.__class__.__name__ == pet_model
        assert result.body.name == pet_name
        assert result.body.tag == pet_tag
        assert result.body.position == 2
        assert result.body.address.__class__.__name__ == address_model
        assert result.body.address.street == pet_street
        assert result.body.address.city == pet_city

    def test_post_pets(self, spec, spec_dict):
        pet_name = "Cat"
        pet_tag = "cats"
        pet_street = "Piekna"
        pet_city = "Warsaw"
        data_json = {
            "name": pet_name,
            "tag": pet_tag,
            "position": 2,
            "address": {
                "street": pet_street,
                "city": pet_city,
            },
            "ears": {
                "healthy": True,
            },
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }
        request = MockRequest(
            "https://development.gigantic-server.com",
            "post",
            "/v1/pets",
            path_pattern="/v1/pets",
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = openapi_request_validator.validate(spec, request)

        assert result.errors == []
        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )
        assert result.security == {}

        schemas = spec_dict["components"]["schemas"]
        pet_model = schemas["PetCreate"]["x-model"]
        address_model = schemas["Address"]["x-model"]
        assert result.body.__class__.__name__ == pet_model
        assert result.body.name == pet_name
        assert result.body.tag == pet_tag
        assert result.body.position == 2
        assert result.body.address.__class__.__name__ == address_model
        assert result.body.address.street == pet_street
        assert result.body.address.city == pet_city

    def test_post_pets_plain_no_schema(self, spec, spec_dict):
        data = "plain text"
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }
        request = MockRequest(
            "https://development.gigantic-server.com",
            "post",
            "/v1/pets",
            path_pattern="/v1/pets",
            data=data,
            headers=headers,
            cookies=cookies,
            mimetype="text/plain",
        )

        with pytest.warns(UserWarning):
            result = openapi_request_validator.validate(spec, request)

        assert result.errors == []
        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )
        assert result.security == {}
        assert result.body == data

    def test_get_pet_unauthorized(self, spec):
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets/1",
            path_pattern="/v1/pets/{petId}",
            view_args={"petId": "1"},
        )

        result = openapi_request_validator.validate(spec, request)

        assert result.errors == [
            InvalidSecurity(),
        ]
        assert result.body is None
        assert result.parameters == Parameters()
        assert result.security is None

    def test_get_pet(self, spec):
        authorization = "Basic " + self.api_key_encoded
        headers = {
            "Authorization": authorization,
        }
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets/1",
            path_pattern="/v1/pets/{petId}",
            view_args={"petId": "1"},
            headers=headers,
        )

        result = openapi_request_validator.validate(spec, request)

        assert result.errors == []
        assert result.body is None
        assert result.parameters == Parameters(
            path={
                "petId": 1,
            },
        )
        assert result.security == {
            "petstore_auth": self.api_key_encoded,
        }


class TestPathItemParamsValidator:
    @pytest.fixture(scope="session")
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
                            "default": {"description": "Return the resource."}
                        }
                    },
                }
            },
        }

    @pytest.fixture(scope="session")
    def spec(self, spec_dict):
        return Spec.create(spec_dict)

    def test_request_missing_param(self, spec):
        request = MockRequest("http://example.com", "get", "/resource")
        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == Parameters()

    def test_request_invalid_param(self, spec):
        request = MockRequest(
            "http://example.com",
            "get",
            "/resource",
            args={"resId": "invalid"},
        )
        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == CastError
        assert result.body is None
        assert result.parameters == Parameters()

    def test_request_valid_param(self, spec):
        request = MockRequest(
            "http://example.com",
            "get",
            "/resource",
            args={"resId": "10"},
        )
        result = openapi_request_validator.validate(spec, request)

        assert len(result.errors) == 0
        assert result.body is None
        assert result.parameters == Parameters(query={"resId": 10})

    def test_request_override_param(self, spec, spec_dict):
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
        request = MockRequest("http://example.com", "get", "/resource")
        result = openapi_request_validator.validate(
            spec, request, base_url="http://example.com"
        )

        assert len(result.errors) == 0
        assert result.body is None
        assert result.parameters == Parameters()

    def test_request_override_param_uniqueness(self, spec, spec_dict):
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
        request = MockRequest("http://example.com", "get", "/resource")
        result = openapi_request_validator.validate(
            spec, request, base_url="http://example.com"
        )

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == Parameters()


class TestResponseValidator:

    host_url = "http://petstore.swagger.io"

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return Spec.create(spec_dict)

    def test_invalid_server(self, spec):
        request = MockRequest("http://petstore.invalid.net/v1", "get", "/")
        response = MockResponse("Not Found", status_code=404)

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_operation(self, spec):
        request = MockRequest(self.host_url, "patch", "/v1/pets")
        response = MockResponse("Not Found", status_code=404)

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == OperationNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_response(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse("Not Found", status_code=409)

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == ResponseNotFound
        assert result.data is None
        assert result.headers == {}

    def test_invalid_content_type(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse("Not Found", mimetype="text/csv")

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MediaTypeNotFound
        assert result.data is None
        assert result.headers == {}

    def test_missing_body(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse(None)

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MissingResponseContent
        assert result.data is None
        assert result.headers == {}

    def test_invalid_media_type(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse("abcde")

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == MediaTypeDeserializeError
        assert result.data is None
        assert result.headers == {}

    def test_invalid_media_type_value(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response = MockResponse("{}")

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidSchemaValue
        assert result.data is None
        assert result.headers == {}

    def test_invalid_value(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/tags")
        response_json = {
            "data": [
                {"id": 1, "name": "Sparky"},
            ],
        }
        response_data = json.dumps(response_json)
        response = MockResponse(response_data)

        result = openapi_response_validator.validate(spec, request, response)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == InvalidSchemaValue
        assert result.data is None
        assert result.headers == {}

    def test_get_pets(self, spec):
        request = MockRequest(self.host_url, "get", "/v1/pets")
        response_json = {
            "data": [
                {
                    "id": 1,
                    "name": "Sparky",
                    "ears": {
                        "healthy": True,
                    },
                },
            ],
        }
        response_data = json.dumps(response_json)
        response = MockResponse(response_data)

        result = openapi_response_validator.validate(spec, request, response)

        assert result.errors == []
        assert isinstance(result.data, BaseModel)
        assert len(result.data.data) == 1
        assert result.data.data[0].id == 1
        assert result.data.data[0].name == "Sparky"
        assert result.headers == {}
