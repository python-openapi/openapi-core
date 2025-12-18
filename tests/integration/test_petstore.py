import json
from base64 import b64encode
from dataclasses import is_dataclass
from datetime import datetime
from urllib.parse import urlencode
from uuid import UUID

import pytest
from isodate.tzinfo import UTC

from openapi_core import unmarshal_request
from openapi_core import unmarshal_response
from openapi_core import validate_request
from openapi_core import validate_response
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.datatypes import Parameters
from openapi_core.deserializing.styles.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestBodyUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestParametersUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestSecurityUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseDataUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseHeadersUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseUnmarshaller,
)
from openapi_core.validation.request.exceptions import MissingRequiredParameter
from openapi_core.validation.request.exceptions import ParameterValidationError
from openapi_core.validation.request.exceptions import (
    RequestBodyValidationError,
)
from openapi_core.validation.request.exceptions import SecurityValidationError
from openapi_core.validation.request.validators import V30RequestBodyValidator
from openapi_core.validation.request.validators import (
    V30RequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V30RequestSecurityValidator,
)
from openapi_core.validation.response.exceptions import InvalidData
from openapi_core.validation.response.exceptions import MissingRequiredHeader
from openapi_core.validation.response.validators import (
    V30ResponseDataValidator,
)
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue


class TestPetstore:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    @pytest.fixture(scope="module")
    def spec_dict(self, v30_petstore_content):
        return v30_petstore_content

    @pytest.fixture(scope="module")
    def spec(self, v30_petstore_spec):
        return v30_petstore_spec

    @pytest.fixture(scope="module")
    def response_unmarshaller(self, spec):
        return V30ResponseUnmarshaller(spec)

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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestBodyUnmarshaller,
        )

        assert result.body is None

        data_json = {
            "data": [],
        }
        data = json.dumps(data_json).encode()
        headers = {
            "Content-Type": "application/json",
            "x-next": "next-url",
        }
        response = MockResponse(data, headers=headers)

        response_result = unmarshal_response(request, response, spec=spec)

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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
        response = MockResponse(data)

        response_result = unmarshal_response(request, response, spec=spec)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert len(response_result.data.data) == 1
        assert response_result.data.data[0].id == 1
        assert response_result.data.data[0].name == "Cat"

    def test_get_pets_response_media_type(self, spec):
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

        data = b"<html>\xb1\xbc</html>"
        response = MockResponse(
            data, status_code=404, content_type="text/html; charset=iso-8859-2"
        )

        response_result = unmarshal_response(request, response, spec=spec)

        assert response_result.errors == []
        assert response_result.data == data.decode("iso-8859-2")

    def test_get_pets_invalid_response(self, spec, response_unmarshaller):
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        response_data = json.dumps(response_data_json).encode()
        response = MockResponse(response_data)

        with pytest.raises(InvalidData) as exc_info:
            validate_response(
                request,
                response,
                spec=spec,
                cls=V30ResponseDataValidator,
            )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

        response_result = response_unmarshaller.unmarshal(request, response)

        assert response_result.errors == [InvalidData()]
        schema_errors = response_result.errors[0].__cause__.schema_errors
        assert response_result.errors[0].__cause__ == InvalidSchemaValue(
            type="object",
            value=response_data_json,
            schema_errors=schema_errors,
        )
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
                "ids": [12, 13],
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

        data_json = {
            "data": [],
        }
        data = json.dumps(data_json).encode()
        response = MockResponse(data)

        response_result = unmarshal_response(request, response, spec=spec)

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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": 20,
                "page": 1,
                "search": "",
                "tags": ["cats", "dogs"],
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

        data_json = {
            "data": [],
        }
        data = json.dumps(data_json).encode()
        response = MockResponse(data)

        response_result = unmarshal_response(request, response, spec=spec)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.data == []

    def test_get_pets_parameter_schema_error(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "1",
            "tags": ",,",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                with pytest.raises(ParameterValidationError) as exc_info:
                    validate_request(
                        request,
                        spec=spec,
                        cls=V30RequestParametersUnmarshaller,
                    )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                with pytest.raises(ParameterValidationError) as exc_info:
                    validate_request(
                        request,
                        spec=spec,
                        cls=V30RequestParametersValidator,
                    )
        assert type(exc_info.value.__cause__) is CastError

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                with pytest.raises(MissingRequiredParameter):
                    validate_request(
                        request,
                        spec=spec,
                        cls=V30RequestParametersValidator,
                    )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

    def test_get_pets_empty_value(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "1",
            "order": "",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                with pytest.raises(ParameterValidationError) as exc_info:
                    validate_request(
                        request,
                        spec=spec,
                        cls=V30RequestParametersValidator,
                    )
        assert type(exc_info.value.__cause__) is EmptyQueryParameterValue

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

    def test_get_pets_allow_empty_value(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/pets"
        query_params = {
            "limit": "20",
            "search": "",
        }

        request = MockRequest(
            host_url,
            "GET",
            "/pets",
            path_pattern=path_pattern,
            args=query_params,
        )

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "page": 1,
                "limit": 20,
                "search": "",
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": None,
                "page": 1,
                "search": "",
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert result.parameters == Parameters(
            query={
                "limit": None,
                "order": "desc",
                "page": 1,
                "search": "",
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        with pytest.warns(
            DeprecationWarning, match="limit parameter is deprecated"
        ):
            with pytest.warns(
                DeprecationWarning,
                match="Use of allowEmptyValue property is deprecated",
            ):
                result = unmarshal_request(
                    request,
                    spec=spec,
                    cls=V30RequestParametersUnmarshaller,
                )

        assert is_dataclass(result.parameters.query["coordinates"])
        assert (
            result.parameters.query["coordinates"].__class__.__name__
            == "Coordinates"
        )
        assert result.parameters.query["coordinates"].lat == coordinates["lat"]
        assert result.parameters.query["coordinates"].lon == coordinates["lon"]

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert is_dataclass(result.parameters.cookie["userdata"])
        assert (
            result.parameters.cookie["userdata"].__class__.__name__
            == "Userdata"
        )
        assert result.parameters.cookie["userdata"].name == "user1"

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestSecurityUnmarshaller,
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
        data = json.dumps(data_json).encode()
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

    @pytest.mark.xfail(
        reason="urlencoded object with oneof not supported",
        strict=True,
    )
    def test_post_urlencoded(self, spec, spec_dict):
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
        data = urlencode(data_json).encode()
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
            content_type="application/x-www-form-urlencoded",
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert is_dataclass(result.parameters.cookie["userdata"])
        assert (
            result.parameters.cookie["userdata"].__class__.__name__
            == "Userdata"
        )
        assert result.parameters.cookie["userdata"].name == "user1"

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestSecurityUnmarshaller,
        )

        assert result.security == {}

    def test_post_no_one_of_schema(self, spec):
        host_url = "https://staging.gigantic-server.com/v1"
        path_pattern = "/v1/pets"
        pet_name = "Cat"
        alias = "kitty"
        data_json = {
            "name": pet_name,
            "alias": alias,
        }
        data = json.dumps(data_json).encode()
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        with pytest.raises(RequestBodyValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
            )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

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
        data = json.dumps(data_json).encode()
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
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
            content_type="text/html",
            headers=headers,
            cookies=cookies,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            header={
                "api-key": self.api_key,
            },
            cookie={
                "user": 123,
            },
        )

        with pytest.raises(RequestBodyValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
            )
        assert type(exc_info.value.__cause__) is MediaTypeNotFound

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
        data = json.dumps(data_json).encode()
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
                request,
                spec=spec,
                cls=V30RequestParametersValidator,
            )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
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
                request,
                spec=spec,
                cls=V30RequestParametersValidator,
            )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
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
            content_type="text/html",
            headers=headers,
            cookies=cookies,
        )

        with pytest.raises(ServerNotFound):
            validate_request(
                request,
                spec=spec,
                cls=V30RequestParametersValidator,
            )

        with pytest.raises(ServerNotFound):
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
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
        data = json.dumps(data_json).encode()
        response = MockResponse(data)

        with pytest.raises(ServerNotFound):
            validate_response(
                request,
                response,
                spec=spec,
                cls=V30ResponseDataValidator,
            )

    def test_get_pet_invalid_security(self, spec):
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

        with pytest.raises(SecurityValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestSecurityValidator,
            )

        assert exc_info.value.__cause__ == SecurityNotFound(
            [["petstore_auth"]]
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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            path={
                "petId": 1,
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestSecurityUnmarshaller,
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
        data = json.dumps(data_json).encode()
        response = MockResponse(data)

        response_result = unmarshal_response(request, response, spec=spec)

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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            path={
                "petId": 1,
            }
        )

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
        response = MockResponse(data, status_code=404)

        response_result = unmarshal_response(request, response, spec=spec)

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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            path={
                "petId": 1,
            }
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestBodyUnmarshaller,
        )

        assert result.body is None

        data = b"imagedata"
        response = MockResponse(data, content_type="image/png")

        response_result = unmarshal_response(request, response, spec=spec)

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

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

        data_json = ["cats", "birds"]
        data = json.dumps(data_json).encode()
        response = MockResponse(data)

        response_result = unmarshal_response(request, response, spec=spec)

        assert response_result.errors == []
        assert response_result.data == data_json

    def test_post_tags_extra_body_properties(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        pet_name = "Dog"
        alias = "kitty"
        data_json = {
            "name": pet_name,
            "alias": alias,
        }
        data = json.dumps(data_json).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        with pytest.raises(RequestBodyValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
            )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

    def test_post_tags_empty_body(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        data_json = {}
        data = json.dumps(data_json).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        with pytest.raises(RequestBodyValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
            )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

    def test_post_tags_wrong_property_type(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        tag_name = 123
        data = json.dumps(tag_name).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        with pytest.raises(RequestBodyValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
            )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

    def test_post_tags_additional_properties(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        pet_name = "Dog"
        data_json = {
            "name": pet_name,
        }
        data = json.dumps(data_json).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
        response = MockResponse(data, status_code=404)

        response_result = unmarshal_response(request, response, spec=spec)

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
        data = json.dumps(data_json).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        data = json.dumps(data_json).encode()
        response = MockResponse(data, status_code=404)

        response_result = unmarshal_response(request, response, spec=spec)

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
        data = json.dumps(data_json).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        response_data = json.dumps(response_data_json).encode()
        response = MockResponse(response_data, status_code=404)

        result = unmarshal_response(
            request,
            response,
            spec=spec,
            cls=V30ResponseDataUnmarshaller,
        )

        assert is_dataclass(result.data)
        assert result.data.code == code
        assert result.data.message == message
        assert result.data.rootCause == rootCause
        assert result.data.additionalinfo == additionalinfo

        response_result = unmarshal_response(request, response, spec=spec)

        assert response_result.errors == []
        assert is_dataclass(response_result.data)
        assert response_result.data.code == code
        assert response_result.data.message == message
        assert response_result.data.rootCause == rootCause
        assert response_result.data.additionalinfo == additionalinfo

    def test_post_tags_urlencoded(self, spec):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        created = "2016-04-16T16:06:05Z"
        pet_name = "Dog"
        data_json = {
            "created": created,
            "name": pet_name,
        }
        data = urlencode(data_json).encode()
        content_type = "application/x-www-form-urlencoded"

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
            content_type=content_type,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
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
        response_data = json.dumps(response_data_json).encode()
        response = MockResponse(response_data, status_code=404)

        result = unmarshal_response(
            request,
            response,
            spec=spec,
            cls=V30ResponseDataUnmarshaller,
        )

        assert is_dataclass(result.data)
        assert result.data.code == code
        assert result.data.message == message
        assert result.data.rootCause == rootCause
        assert result.data.additionalinfo == additionalinfo

        response_result = unmarshal_response(request, response, spec=spec)

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
        data = json.dumps(data_json).encode()

        request = MockRequest(
            host_url,
            "POST",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        with pytest.raises(RequestBodyValidationError) as exc_info:
            validate_request(
                request,
                spec=spec,
                cls=V30RequestBodyValidator,
            )
        assert type(exc_info.value.__cause__) is InvalidSchemaValue

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
        data = json.dumps(data_json).encode()
        response = MockResponse(data, status_code=404)

        response_result = unmarshal_response(request, response, spec=spec)

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
        data = json.dumps(data_json).encode()
        request = MockRequest(
            host_url,
            "DELETE",
            "/tags",
            path_pattern=path_pattern,
            data=data,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert is_dataclass(result.body)
        assert result.body.ids == ids

        data = None
        headers = {
            "x-delete-confirm": "true",
        }
        response = MockResponse(data, status_code=200, headers=headers)

        with pytest.warns(
            DeprecationWarning, match="x-delete-confirm header is deprecated"
        ):
            response_result = unmarshal_response(request, response, spec=spec)
        assert response_result.errors == []
        assert response_result.data is None

        with pytest.warns(
            DeprecationWarning, match="x-delete-confirm header is deprecated"
        ):
            result = unmarshal_response(
                request,
                response,
                spec=spec,
                cls=V30ResponseHeadersUnmarshaller,
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

        validate_request(request, spec=spec)

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

    @pytest.mark.parametrize(
        "header_value,expexted_value",
        [
            ("y", True),
            ("t", True),
            ("yes", True),
            ("on", True),
            ("true", True),
            ("1", True),
            ("n", False),
            ("f", False),
            ("no", False),
            ("off", False),
            ("false", False),
            ("0", False),
        ],
    )
    def test_delete_tags_header(self, spec, header_value, expexted_value):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        headers = {
            "x-delete-force": header_value,
        }
        request = MockRequest(
            host_url,
            "DELETE",
            "/tags",
            headers=headers,
            path_pattern=path_pattern,
        )

        validate_request(request, spec=spec)

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters(
            header={
                "x-delete-force": expexted_value,
            },
        )

    def test_delete_tags_raises_missing_required_response_header(
        self, spec, response_unmarshaller
    ):
        host_url = "http://petstore.swagger.io/v1"
        path_pattern = "/v1/tags"
        request = MockRequest(
            host_url,
            "DELETE",
            "/tags",
            path_pattern=path_pattern,
        )

        result = unmarshal_request(
            request,
            spec=spec,
            cls=V30RequestParametersUnmarshaller,
        )

        assert result.parameters == Parameters()

        result = unmarshal_request(
            request, spec=spec, cls=V30RequestBodyUnmarshaller
        )

        assert result.body is None

        data = None
        response = MockResponse(data, status_code=200)

        with pytest.warns(DeprecationWarning):
            response_result = response_unmarshaller.unmarshal(
                request, response
            )

        assert response_result.errors == [
            MissingRequiredHeader(name="x-delete-confirm"),
        ]
        assert response_result.data is None
