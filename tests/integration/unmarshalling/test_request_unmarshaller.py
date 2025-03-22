import json
from base64 import b64encode

import pytest

from openapi_core import V30RequestUnmarshaller
from openapi_core.datatypes import Parameters
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.testing import MockRequest
from openapi_core.validation.request.exceptions import InvalidParameter
from openapi_core.validation.request.exceptions import MissingRequiredParameter
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
)
from openapi_core.validation.request.exceptions import (
    RequestBodyValidationError,
)
from openapi_core.validation.request.exceptions import SecurityValidationError


class TestRequestUnmarshaller:
    host_url = "http://petstore.swagger.io"

    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    @pytest.fixture(scope="session")
    def spec_dict(self, v30_petstore_content):
        return v30_petstore_content

    @pytest.fixture(scope="session")
    def spec(self, v30_petstore_spec):
        return v30_petstore_spec

    @pytest.fixture(scope="session")
    def request_unmarshaller(self, spec):
        return V30RequestUnmarshaller(spec)

    def test_request_server_error(self, request_unmarshaller):
        request = MockRequest("http://petstore.invalid.net/v1", "get", "/")

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.body is None
        assert result.parameters == Parameters()

    def test_invalid_path(self, request_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1")

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == PathNotFound
        assert result.body is None
        assert result.parameters == Parameters()

    def test_invalid_operation(self, request_unmarshaller):
        request = MockRequest(self.host_url, "patch", "/v1/pets")

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == OperationNotFound
        assert result.body is None
        assert result.parameters == Parameters()

    def test_missing_parameter(self, request_unmarshaller):
        request = MockRequest(self.host_url, "get", "/v1/pets")

        with pytest.warns(DeprecationWarning):
            result = request_unmarshaller.unmarshal(request)

        assert type(result.errors[0]) == MissingRequiredParameter
        assert result.body is None
        assert result.parameters == Parameters(
            query={
                "page": 1,
                "search": "",
            },
        )

    def test_get_pets(self, request_unmarshaller):
        args = {"limit": "10", "ids": ["1", "2"], "api_key": self.api_key}
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets",
            path_pattern="/v1/pets",
            args=args,
        )

        with pytest.warns(DeprecationWarning):
            result = request_unmarshaller.unmarshal(request)

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

    def test_get_pets_multidict(self, request_unmarshaller):
        from multidict import MultiDict

        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets",
            path_pattern="/v1/pets",
        )
        request.parameters.query = MultiDict(
            [("limit", "5"), ("ids", "1"), ("ids", "2")],
        )

        with pytest.warns(DeprecationWarning):
            result = request_unmarshaller.unmarshal(request)

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

    def test_missing_body(self, request_unmarshaller):
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

        result = request_unmarshaller.unmarshal(request)

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

    def test_invalid_content_type(self, request_unmarshaller):
        data = b"csv,data"
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
            content_type="text/csv",
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) == RequestBodyValidationError
        assert result.errors[0].__cause__ == MediaTypeNotFound(
            mimetype="text/csv",
            availableMimetypes=[
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain",
            ],
        )
        assert result.body is None
        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

    def test_invalid_complex_parameter(self, request_unmarshaller, spec_dict):
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
        data = json.dumps(data_json).encode()
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

        result = request_unmarshaller.unmarshal(request)

        assert result.errors == [
            InvalidParameter(name="userdata", location="cookie")
        ]
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

    def test_post_pets(self, request_unmarshaller, spec_dict):
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
        data = json.dumps(data_json).encode()
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

        result = request_unmarshaller.unmarshal(request)

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

    def test_post_pets_plain_no_schema(self, request_unmarshaller):
        data = b"plain text"
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
            content_type="text/plain",
        )

        result = request_unmarshaller.unmarshal(request)

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
        assert result.body == data.decode()

    def test_get_pet_unauthorized(self, request_unmarshaller):
        request = MockRequest(
            self.host_url,
            "get",
            "/v1/pets/1",
            path_pattern="/v1/pets/{petId}",
            view_args={"petId": "1"},
        )

        result = request_unmarshaller.unmarshal(request)

        assert len(result.errors) == 1
        assert type(result.errors[0]) is SecurityValidationError
        assert result.errors[0].__cause__ == SecurityNotFound(
            [["petstore_auth"]]
        )
        assert result.body is None
        assert result.parameters == Parameters()
        assert result.security is None

    def test_get_pet(self, request_unmarshaller):
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

        result = request_unmarshaller.unmarshal(request)

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
