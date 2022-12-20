import json
from base64 import b64encode
from dataclasses import is_dataclass
from dataclasses import make_dataclass
from datetime import datetime
from uuid import UUID

import pytest
from isodate.tzinfo import UTC

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.parameters.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.spec import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.exceptions import MissingRequiredHeader
from openapi_core.validation.exceptions import MissingRequiredParameter
from openapi_core.validation.request import openapi_v30_request_body_validator
from openapi_core.validation.request import (
    openapi_v30_request_parameters_validator,
)
from openapi_core.validation.request import (
    openapi_v30_request_security_validator,
)
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.response import (
    openapi_v30_response_data_validator,
)
from openapi_core.validation.response import (
    openapi_v30_response_headers_validator,
)
from openapi_core.validation.response import openapi_v30_response_validator
from openapi_core.validation.shortcuts import validate_request
from openapi_core.validation.shortcuts import validate_response


class TestPetstore:

    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    @pytest.fixture(scope="module")
    def spec_uri(self):
        return "file://tests/integration/data/v3.0/petstore.yaml"

    @pytest.fixture(scope="module")
    def spec_dict(self, factory):
        content, _ = factory.content_from_file("data/v3.0/petstore.yaml")
        return content

    @pytest.fixture(scope="module")
    def spec(self, spec_dict, spec_uri):
        return Spec.create(spec_dict, url=spec_uri)

    def test_get_pets(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "20",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data_json = {
            "data": [],
        }
        data = json.dumps(data_json)
        headers = {
            "Content-Type": "application/json",
            "x-next": "next-url",
        }
        response = MockResponse(data, headers=headers)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.data == []
        assert response_result.headers == {
            "x-next": "next-url",
        }

    def test_get_pets_response(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "20",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data_json = {
            "data": [
                {
                    "id": 1,
                    "name": "Cat",
                    "ears": {
                        "healthy": True,
                    },
                }
            ],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert len(response_result.data.data) == 1
        assert response_result.data.data[0].id == 1
        assert response_result.data.data[0].name == "Cat"

    def test_get_pets_response_no_schema(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "20",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data = "<html></html>"
        response = MockResponse(data, status_code=404, mimetype="text/html")

        with pytest.warns(UserWarning):
            response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert response_result.data == data

    def test_get_pets_invalid_response(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "20",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        response_data_json = {
            "data": [
                {
                    "id": 1,
                    "name": {
                        "first_name": "Cat",
                    },
                }
            ],
        }
        response_data = json.dumps(response_data_json)
        response = MockResponse(response_data)

        with pytest.raises(InvalidSchemaValue):
            validate_response(
                spec,
                request,
                response,
                validator=openapi_v30_response_data_validator,
            )

        response_result = openapi_v30_response_validator.validate(
            spec, request, response
        )

        schema_errors = response_result.errors[0].schema_errors
        assert response_result.errors == [
            InvalidSchemaValue(
                type="object",
                value=response_data_json,
                schema_errors=schema_errors,
            ),
        ]
        assert response_result.data is None

    def test_get_pets_ids_param(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "20",
            "ids": ["12", "13"],
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
                "ids": [12, 13],
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data_json = {
            "data": [],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.data == []

    def test_get_pets_tags_param(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = [
            ("limit", "20"),
            ("tags", "cats,dogs"),
        ]

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
                "tags": ["cats", "dogs"],
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data_json = {
            "data": [],
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.data == []

    def test_get_pets_parameter_deserialization_error(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": 1,
            "tags": 12,
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            with pytest.raises(DeserializeError):
                validate_request(
                    spec,
                    request,
                    validator=openapi_v30_request_parameters_validator,
                )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_wrong_parameter_type(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "twenty",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            with pytest.raises(CastError):
                validate_request(
                    spec,
                    request,
                    validator=openapi_v30_request_parameters_validator,
                )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_raises_missing_required_param(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
        )

        with pytest.warns(DeprecationWarning):
            with pytest.raises(MissingRequiredParameter):
                validate_request(
                    spec,
                    request,
                    validator=openapi_v30_request_parameters_validator,
                )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_empty_value(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            with pytest.raises(EmptyQueryParameterValue):
                validate_request(
                    spec,
                    request,
                    validator=openapi_v30_request_parameters_validator,
                )
        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_allow_empty_value(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": 20,
            "search": "",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "page": 1,
                "limit": 20,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_none_value(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": None,
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": None,
                "page": 1,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_param_order(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": None,
            "order": "desc",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert result.parameters == Parameters(
            query={
                "limit": None,
                "order": "desc",
                "page": 1,
                "search": "",
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_get_pets_param_coordinates(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        coordinates = {
            "lat": 1.12,
            "lon": 32.12,
        }
        query_params = {
            "limit": None,
            "coordinates": json.dumps(coordinates),
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        assert is_dataclass(result.parameters.query["coordinates"])
        assert (
            result.parameters.query["coordinates"].__class__.__name__
            == "Coordinates"
        )
        assert result.parameters.query["coordinates"].lat == coordinates["lat"]
        assert result.parameters.query["coordinates"].lon == coordinates["lon"]

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_post_birds(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        pet_tag = "cats"
        pet_street = "Piekna"
        pet_city = "Warsaw"
        pet_healthy = False
        data_json = {
            "name": pet_name,
            "tag": pet_tag,
            "position": 2,
            "address": {
                "street": pet_street,
                "city": pet_city,
            },
            "healthy": pet_healthy,
            "wings": {
                "healthy": pet_healthy,
            },
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }
        userdata = {
            "name": "user1",
        }
        userdata_json = json.dumps(userdata)
        cookies = {
            "user": "123",
            "userdata": userdata_json,
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert is_dataclass(result.parameters.cookie["userdata"])
        assert (
            result.parameters.cookie["userdata"].__class__.__name__
            == "Userdata"
        )
        assert result.parameters.cookie["userdata"].name == "user1"

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

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
        assert result.body.healthy == pet_healthy

        result = validate_request(
            spec, request, validator=openapi_v30_request_security_validator
        )

        assert result.security == {}

    def test_post_cats(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        pet_tag = "cats"
        pet_street = "Piekna"
        pet_city = "Warsaw"
        pet_healthy = False
        data_json = {
            "name": pet_name,
            "tag": pet_tag,
            "position": 2,
            "address": {
                "street": pet_street,
                "city": pet_city,
            },
            "healthy": pet_healthy,
            "ears": {
                "healthy": pet_healthy,
            },
            "extra": None,
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

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
        assert result.body.healthy == pet_healthy
        assert result.body.extra is None

    def test_post_cats_boolean_string(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        pet_tag = "cats"
        pet_street = "Piekna"
        pet_city = "Warsaw"
        pet_healthy = False
        data_json = {
            "name": pet_name,
            "tag": pet_tag,
            "position": 2,
            "address": {
                "street": pet_street,
                "city": pet_city,
            },
            "healthy": pet_healthy,
            "ears": {
                "healthy": pet_healthy,
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
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

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
        assert result.body.healthy is False

    def test_post_no_one_of_schema(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        alias = "kitty"
        data_json = {
            "name": pet_name,
            "alias": alias,
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        with pytest.raises(InvalidSchemaValue):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

    def test_post_cats_only_required_body(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        pet_healthy = True
        data_json = {
            "name": pet_name,
            "ears": {
                "healthy": pet_healthy,
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
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            headers=headers,
            cookies=cookies,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        schemas = spec_dict["components"]["schemas"]
        pet_model = schemas["PetCreate"]["x-model"]
        assert result.body.__class__.__name__ == pet_model
        assert result.body.name == pet_name
        assert not hasattr(result.body, "tag")
        assert not hasattr(result.body, "address")

    def test_post_pets_raises_invalid_mimetype(self, spec):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        data_json = {
            "name": "Cat",
            "tag": "cats",
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }
        cookies = {
            "user": "123",
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            mimetype="text/html",
            headers=headers,
            cookies=cookies,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        with pytest.raises(MediaTypeNotFound):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

    def test_post_pets_missing_cookie(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        pet_healthy = True
        data_json = {
            "name": pet_name,
            "ears": {
                "healthy": pet_healthy,
            },
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": self.api_key_encoded,
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            headers=headers,
        )

        with pytest.raises(MissingRequiredParameter):
            validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        schemas = spec_dict["components"]["schemas"]
        pet_model = schemas["PetCreate"]["x-model"]
        assert result.body.__class__.__name__ == pet_model
        assert result.body.name == pet_name
        assert not hasattr(result.body, "tag")
        assert not hasattr(result.body, "address")

    def test_post_pets_missing_header(self, spec, spec_dict):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        pet_healthy = True
        data_json = {
            "name": pet_name,
            "ears": {
                "healthy": pet_healthy,
            },
        }
        data = json.dumps(data_json)
        cookies = {
            "user": "123",
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            cookies=cookies,
        )

        with pytest.raises(MissingRequiredParameter):
            validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        schemas = spec_dict["components"]["schemas"]
        pet_model = schemas["PetCreate"]["x-model"]
        assert result.body.__class__.__name__ == pet_model
        assert result.body.name == pet_name
        assert not hasattr(result.body, "tag")
        assert not hasattr(result.body, "address")

    def test_post_pets_raises_invalid_server_error(self, spec):
        host_url = "http://flowerstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        data_json = {
            "name": "Cat",
            "tag": "cats",
        }
        data = json.dumps(data_json)
        headers = {
            "api-key": "12345",
        }
        cookies = {
            "user": "123",
        }

        request = MockRequest(
            host_url,
            "POST",
            "/pets",
            path_pattern=path_pattern,
            data=data,
            mimetype="text/html",
            headers=headers,
            cookies=cookies,
        )

        with pytest.raises(ServerNotFound):
            validate_request(
                spec,
                request,
                validator=openapi_v30_request_parameters_validator,
            )

        with pytest.raises(ServerNotFound):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

        data_id = 1
        data_name = "test"
        data_json = {
            "data": {
                "id": data_id,
                "name": data_name,
                "ears": {
                    "healthy": True,
                },
            },
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        with pytest.raises(ServerNotFound):
            validate_response(
                spec,
                request,
                response,
                validator=openapi_v30_response_data_validator,
            )

    def test_get_pet(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets/{petId}"
        view_args = {
            "petId": "1",
        }
        auth = "authuser"
        headers = {
            "Authorization": f"Basic {auth}",
        }
        request = MockRequest(
            host_url,
            "GET",
            "/pets/1",
            path_pattern=path_pattern,
            view_args=view_args,
            headers=headers,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            path={
                "petId": 1,
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        result = validate_request(
            spec, request, validator=openapi_v30_request_security_validator
        )

        assert result.security == {
            "petstore_auth": auth,
        }

        data_id = 1
        data_name = "test"
        data_json = {
            "data": {
                "id": data_id,
                "name": data_name,
                "ears": {
                    "healthy": True,
                },
            },
        }
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert is_dataclass(response_result.data.data)
        assert response_result.data.data.id == data_id
        assert response_result.data.data.name == data_name

    def test_get_pet_not_found(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets/{petId}"
        view_args = {
            "petId": "1",
        }
        request = MockRequest(
            host_url,
            "GET",
            "/pets/1",
            path_pattern=path_pattern,
            view_args=view_args,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            path={
                "petId": 1,
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        code = 404
        message = "Not found"
        rootCause = "Pet not found"
        data_json = {
            "code": 404,
            "message": message,
            "rootCause": rootCause,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause

    def test_get_pet_wildcard(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets/{petId}"
        view_args = {
            "petId": "1",
        }
        request = MockRequest(
            host_url,
            "GET",
            "/pets/1",
            path_pattern=path_pattern,
            view_args=view_args,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters(
            path={
                "petId": 1,
            }
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data = b"imagedata"
        response = MockResponse(data, mimetype="image/png")

        with pytest.warns(UserWarning):
            response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert response_result.data == data

    def test_get_tags(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"

        request = MockRequest(
            host_url,
            "GET",
            "/tags",
            path_pattern=path_pattern,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data_json = ["cats", "birds"]
        data = json.dumps(data_json)
        response = MockResponse(data)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert response_result.data == data_json

    def test_post_tags_extra_body_properties(self, spec, spec_dict):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        pet_name = "Dog"
        alias = "kitty"
        data_json = {
            "name": pet_name,
            "alias": alias,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        with pytest.raises(InvalidSchemaValue):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

    def test_post_tags_empty_body(self, spec, spec_dict):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        data_json = {}
        data = json.dumps(data_json)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        with pytest.raises(InvalidSchemaValue):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

    def test_post_tags_wrong_property_type(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        tag_name = 123
        data = json.dumps(tag_name)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        with pytest.raises(InvalidSchemaValue):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

    def test_post_tags_additional_properties(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        pet_name = "Dog"
        data_json = {
            "name": pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert is_dataclass(result.body)
        assert result.body.name == pet_name

        code = 400
        message = "Bad request"
        rootCause = "Tag already exist"
        additionalinfo = "Tag Dog already exist"
        data_json = {
            "code": code,
            "message": message,
            "rootCause": rootCause,
            "additionalinfo": additionalinfo,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_created_now(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        created = "now"
        pet_name = "Dog"
        data_json = {
            "created": created,
            "name": pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert is_dataclass(result.body)
        assert result.body.created == created
        assert result.body.name == pet_name

        code = 400
        message = "Bad request"
        rootCause = "Tag already exist"
        additionalinfo = "Tag Dog already exist"
        data_json = {
            "code": 400,
            "message": "Bad request",
            "rootCause": "Tag already exist",
            "additionalinfo": "Tag Dog already exist",
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_created_datetime(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        created = "2016-04-16T16:06:05Z"
        pet_name = "Dog"
        data_json = {
            "created": created,
            "name": pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert is_dataclass(result.body)
        assert result.body.created == datetime(
            2016, 4, 16, 16, 6, 5, tzinfo=UTC
        )
        assert result.body.name == pet_name

        code = 400
        message = "Bad request"
        rootCause = "Tag already exist"
        additionalinfo = "Tag Dog already exist"
        response_data_json = {
            "code": code,
            "message": message,
            "rootCause": rootCause,
            "additionalinfo": additionalinfo,
        }
        response_data = json.dumps(response_data_json)
        response = MockResponse(response_data, status_code=404)

        result = validate_response(
            spec,
            request,
            response,
            validator=openapi_v30_response_data_validator,
        )

        assert is_dataclass(result.data)
        assert result.data.code == code
        assert result.data.message == message
        assert result.data.rootCause == rootCause
        assert result.data.additionalinfo == additionalinfo

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_created_invalid_type(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        created = "long time ago"
        pet_name = "Dog"
        data_json = {
            "created": created,
            "name": pet_name,
        }
        data = json.dumps(data_json)

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        with pytest.raises(InvalidSchemaValue):
            validate_request(
                spec, request, validator=openapi_v30_request_body_validator
            )

        code = 400
        message = "Bad request"
        correlationId = UUID("a8098c1a-f86e-11da-bd1a-00112444be1e")
        rootCause = "Tag already exist"
        additionalinfo = "Tag Dog already exist"
        data_json = {
            "message": message,
            "correlationId": str(correlationId),
            "rootCause": rootCause,
            "additionalinfo": additionalinfo,
        }
        data = json.dumps(data_json)
        response = MockResponse(data, status_code=404)

        response_result = validate_response(spec, request, response)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.correlationId == correlationId
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_delete_tags_with_requestbody(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        ids = [1, 2, 3]
        data_json = {
            "ids": ids,
        }
        data = json.dumps(data_json)
        request = MockRequest(
            host_url,
            "DELETE",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert is_dataclass(result.body)
        assert result.body.ids == ids

        data = None
        headers = {
            "x-delete-confirm": "true",
        }
        response = MockResponse(data, status_code=200, headers=headers)

        with pytest.warns(DeprecationWarning):
            response_result = validate_response(spec, request, response)
        assert response_result.errors == []
        assert response_result.data is None

        with pytest.warns(DeprecationWarning):
            result = validate_response(
                spec,
                request,
                response,
                validator=openapi_v30_response_headers_validator,
            )

        assert result.headers == {
            "x-delete-confirm": True,
        }

    def test_delete_tags_no_requestbody(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        request = MockRequest(
            host_url,
            "DELETE",
            "/tags",
            path_pattern=path_pattern,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

    def test_delete_tags_raises_missing_required_response_header(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        request = MockRequest(
            host_url,
            "DELETE",
            "/tags",
            path_pattern=path_pattern,
        )

        result = validate_request(
            spec, request, validator=openapi_v30_request_parameters_validator
        )

        assert result.parameters == Parameters()

        result = validate_request(
            spec, request, validator=openapi_v30_request_body_validator
        )

        assert result.body is None

        data = None
        response = MockResponse(data, status_code=200)

        with pytest.warns(DeprecationWarning):
            response_result = openapi_v30_response_validator.validate(
                spec, request, response
            )

        assert response_result.errors == [
            MissingRequiredHeader(name="x-delete-confirm"),
        ]
        assert response_result.data is None
