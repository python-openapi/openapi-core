from base64 import b64encode
from json import dumps

import pytest
from urllib3 import encode_multipart_formdata


class BaseTestFalconProject:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class TestPetListResource(BaseTestFalconProject):
    def test_get_no_required_param(self, client):
        headers = {
            "Content-Type": "application/json",
        }

        with pytest.warns(DeprecationWarning):
            response = client.simulate_get(
                "/v1/pets", host="petstore.swagger.io", headers=headers
            )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.validation.request.exceptions."
                        "MissingRequiredParameter'>"
                    ),
                    "status": 400,
                    "title": "Missing required query parameter: limit",
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_get_valid(self, client):
        headers = {
            "Content-Type": "application/json",
        }
        query_string = "limit=12"

        with pytest.warns(DeprecationWarning):
            response = client.simulate_get(
                "/v1/pets",
                host="petstore.swagger.io",
                headers=headers,
                query_string=query_string,
            )

        assert response.status_code == 200
        assert response.json == {
            "data": [
                {
                    "id": 12,
                    "name": "Cat",
                    "ears": {
                        "healthy": True,
                    },
                },
            ],
        }

    def test_get_valid_multiple_ids(self, client):
        headers = {
            "Content-Type": "application/json",
        }
        query_string = "limit=2&ids=1&ids=2"

        with pytest.warns(DeprecationWarning):
            response = client.simulate_get(
                "/v1/pets",
                host="petstore.swagger.io",
                headers=headers,
                query_string=query_string,
            )

        assert response.status_code == 200
        assert response.json == {
            "data": [
                {
                    "id": 12,
                    "name": "Cat",
                    "ears": {
                        "healthy": True,
                    },
                },
            ],
        }

    def test_post_server_invalid(self, client):
        response = client.simulate_post(
            "/v1/pets",
            host="petstore.swagger.io",
        )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    "status": 400,
                    "title": (
                        "Server not found for "
                        "http://petstore.swagger.io/v1/pets"
                    ),
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_post_required_header_param_missing(self, client):
        cookies = {"user": 1}
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
        content_type = "application/json"
        headers = {
            "Authorization": "Basic testuser",
            "Content-Type": content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            "/v1/pets",
            host="staging.gigantic-server.com",
            headers=headers,
            body=body,
            cookies=cookies,
            protocol="https",
        )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.validation.request.exceptions."
                        "MissingRequiredParameter'>"
                    ),
                    "status": 400,
                    "title": "Missing required header parameter: api-key",
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_post_media_type_invalid(self, client):
        cookies = {"user": 1}
        data_json = {
            "data": "",
        }
        # noly 3 media types are supported by falcon by default:
        # json, multipart and urlencoded
        content_type = "application/vnd.api+json"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            "/v1/pets",
            host="staging.gigantic-server.com",
            headers=headers,
            body=body,
            cookies=cookies,
            protocol="https",
        )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.templating.media_types."
                        "exceptions.MediaTypeNotFound'>"
                    ),
                    "status": 415,
                    "title": (
                        "Content for the following mimetype not found: "
                        f"{content_type}. "
                        "Valid mimetypes: ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']"
                    ),
                }
            ]
        }
        assert response.status_code == 415
        assert response.json == expected_data

    def test_post_required_cookie_param_missing(self, client):
        content_type = "application/json"
        data_json = {
            "id": 12,
            "name": "Cat",
            "ears": {
                "healthy": True,
            },
        }
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            "/v1/pets",
            host="staging.gigantic-server.com",
            headers=headers,
            body=body,
            protocol="https",
        )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.validation.request.exceptions."
                        "MissingRequiredParameter'>"
                    ),
                    "status": 400,
                    "title": "Missing required cookie parameter: user",
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    @pytest.mark.parametrize(
        "data_json",
        [
            {
                "id": 12,
                "name": "Cat",
                "ears": {
                    "healthy": True,
                },
            },
            {
                "id": 12,
                "name": "Bird",
                "wings": {
                    "healthy": True,
                },
            },
        ],
    )
    def test_post_valid(self, client, data_json):
        cookies = {"user": 1}
        content_type = "application/json"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }
        body = dumps(data_json)

        response = client.simulate_post(
            "/v1/pets",
            host="staging.gigantic-server.com",
            headers=headers,
            body=body,
            cookies=cookies,
            protocol="https",
        )

        assert response.status_code == 201
        assert not response.content

    @pytest.mark.xfail(
        reason="falcon multipart form serialization unsupported",
        strict=True,
    )
    def test_post_multipart_valid(self, client, data_gif):
        cookies = {"user": 1}
        auth = "authuser"
        fields = {
            "name": "Cat",
            "address": (
                "aaddress.json",
                dumps(dict(city="Warsaw")),
                "application/json",
            ),
            "photo": (
                "photo.jpg",
                data_gif,
                "image/jpeg",
            ),
        }
        body, content_type_header = encode_multipart_formdata(fields)
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": content_type_header,
        }

        response = client.simulate_post(
            "/v1/pets",
            host="staging.gigantic-server.com",
            headers=headers,
            body=body,
            cookies=cookies,
            protocol="https",
        )

        assert response.status_code == 200


class TestPetDetailResource:
    def test_get_server_invalid(self, client):
        headers = {"Content-Type": "application/json"}

        response = client.simulate_get("/v1/pets/12", headers=headers)

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    "status": 400,
                    "title": (
                        "Server not found for "
                        "http://falconframework.org/v1/pets/12"
                    ),
                }
            ]
        }
        assert response.status_code == 400
        assert response.json == expected_data

    def test_get_path_invalid(self, client):
        headers = {"Content-Type": "application/json"}

        response = client.simulate_get(
            "/v1/pet/invalid", host="petstore.swagger.io", headers=headers
        )

        assert response.status_code == 404

    def test_get_unauthorized(self, client):
        headers = {"Content-Type": "application/json"}

        response = client.simulate_get(
            "/v1/pets/12", host="petstore.swagger.io", headers=headers
        )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.templating.security.exceptions."
                        "SecurityNotFound'>"
                    ),
                    "status": 403,
                    "title": (
                        "Security not found. Schemes not valid for any "
                        "requirement: [['petstore_auth']]"
                    ),
                }
            ]
        }
        assert response.status_code == 403
        assert response.json == expected_data

    def test_get_valid(self, client):
        auth = "authuser"
        content_type = "application/json"
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": content_type,
        }

        response = client.simulate_get(
            "/v1/pets/12", host="petstore.swagger.io", headers=headers
        )

        assert response.status_code == 200

    def test_delete_method_invalid(self, client):
        auth = "authuser"
        content_type = "application/json"
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": content_type,
        }

        response = client.simulate_delete(
            "/v1/pets/12", host="petstore.swagger.io", headers=headers
        )

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "OperationNotFound'>"
                    ),
                    "status": 405,
                    "title": (
                        "Operation delete not found for "
                        "http://petstore.swagger.io/v1/pets/12"
                    ),
                }
            ]
        }
        assert response.status_code == 405
        assert response.json == expected_data


class TestPetPhotoResource(BaseTestFalconProject):
    def test_get_valid(self, client, data_gif):
        cookies = {"user": 1}
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
        }

        response = client.simulate_get(
            "/v1/pets/1/photo",
            host="petstore.swagger.io",
            headers=headers,
            cookies=cookies,
        )

        assert response.content == data_gif
        assert response.status_code == 200

    @pytest.mark.xfail(
        reason="falcon request binary handler not implemented",
        strict=True,
    )
    def test_post_valid(self, client, data_gif):
        cookies = {"user": 1}
        content_type = "image/jpeg"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }

        response = client.simulate_post(
            "/v1/pets/1/photo",
            host="petstore.swagger.io",
            headers=headers,
            body=data_gif,
            cookies=cookies,
        )

        assert not response.content
        assert response.status_code == 201
