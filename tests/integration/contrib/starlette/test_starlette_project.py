import os
import sys
from base64 import b64encode

import pytest
from starlette.testclient import TestClient


@pytest.fixture(autouse=True, scope="module")
def project_setup():
    directory = os.path.abspath(os.path.dirname(__file__))
    project_dir = os.path.join(directory, "data/v3.0")
    sys.path.insert(0, project_dir)
    yield
    sys.path.remove(project_dir)


class BaseTestPetstore:
    api_key = "12345"

    @pytest.fixture
    def app(self):
        from starletteproject.__main__ import app

        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app, base_url="http://petstore.swagger.io")

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class BaseTestPetstoreSkipReponse:

    @pytest.fixture
    def app(self):
        from starletteproject.__main__ import app_skip_response

        return app_skip_response

    @pytest.fixture
    def client(self, app):
        return TestClient(app, base_url="http://petstore.swagger.io")


class TestPetListEndpoint(BaseTestPetstore):
    def test_get_no_required_param(self, client):
        headers = {
            "Authorization": "Basic testuser",
        }

        with pytest.warns(DeprecationWarning):
            response = client.get("/v1/pets", headers=headers)

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
        assert response.json() == expected_data

    def test_get_valid(self, client):
        data_json = {
            "limit": 12,
        }
        headers = {
            "Authorization": "Basic testuser",
        }

        with pytest.warns(DeprecationWarning):
            response = client.get(
                "/v1/pets",
                params=data_json,
                headers=headers,
            )

        expected_data = {
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
        assert response.status_code == 200
        assert response.json() == expected_data

    def test_post_server_invalid(self, client):
        response = client.post("/v1/pets")

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
        assert response.json() == expected_data

    def test_post_required_header_param_missing(self, client):
        client.cookies.set("user", "1")
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
        response = client.post(
            "https://staging.gigantic-server.com/v1/pets",
            json=data_json,
            headers=headers,
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
        assert response.json() == expected_data

    def test_post_media_type_invalid(self, client):
        client.cookies.set("user", "1")
        content = "data"
        content_type = "text/html"
        headers = {
            "Authorization": "Basic testuser",
            "Content-Type": content_type,
            "Api-Key": self.api_key_encoded,
        }
        response = client.post(
            "https://staging.gigantic-server.com/v1/pets",
            content=content,
            headers=headers,
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
                        "text/html. "
                        "Valid mimetypes: ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']"
                    ),
                }
            ]
        }
        assert response.status_code == 415
        assert response.json() == expected_data

    def test_post_required_cookie_param_missing(self, client):
        data_json = {
            "id": 12,
            "name": "Cat",
            "ears": {
                "healthy": True,
            },
        }
        content_type = "application/json"
        headers = {
            "Authorization": "Basic testuser",
            "Content-Type": content_type,
            "Api-Key": self.api_key_encoded,
        }
        response = client.post(
            "https://staging.gigantic-server.com/v1/pets",
            json=data_json,
            headers=headers,
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
        assert response.json() == expected_data

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
        client.cookies.set("user", "1")
        content_type = "application/json"
        headers = {
            "Authorization": "Basic testuser",
            "Content-Type": content_type,
            "Api-Key": self.api_key_encoded,
        }
        response = client.post(
            "https://staging.gigantic-server.com/v1/pets",
            json=data_json,
            headers=headers,
        )

        assert response.status_code == 201
        assert not response.content


class TestPetDetailEndpoint(BaseTestPetstore):
    def test_get_server_invalid(self, client):
        response = client.get("http://testserver/v1/pets/12")

        expected_data = {
            "errors": [
                {
                    "type": (
                        "<class 'openapi_core.templating.paths.exceptions."
                        "ServerNotFound'>"
                    ),
                    "status": 400,
                    "title": (
                        "Server not found for " "http://testserver/v1/pets/12"
                    ),
                }
            ]
        }
        assert response.status_code == 400
        assert response.json() == expected_data

    def test_get_unauthorized(self, client):
        response = client.get("/v1/pets/12")

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
        assert response.json() == expected_data

    def test_delete_method_invalid(self, client):
        headers = {
            "Authorization": "Basic testuser",
        }
        response = client.delete("/v1/pets/12", headers=headers)

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
        assert response.json() == expected_data

    def test_get_valid(self, client):
        headers = {
            "Authorization": "Basic testuser",
        }
        response = client.get("/v1/pets/12", headers=headers)

        expected_data = {
            "data": {
                "id": 12,
                "name": "Cat",
                "ears": {
                    "healthy": True,
                },
            },
        }
        assert response.status_code == 200
        assert response.json() == expected_data


class TestPetPhotoEndpoint(BaseTestPetstore):
    def test_get_valid(self, client, data_gif):
        client.cookies.set("user", "1")
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
        }

        response = client.get(
            "/v1/pets/1/photo",
            headers=headers,
        )

        assert response.content == data_gif
        assert response.status_code == 200

    def test_post_valid(self, client, data_gif):
        client.cookies.set("user", "1")
        content_type = "image/gif"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }

        response = client.post(
            "/v1/pets/1/photo",
            headers=headers,
            content=data_gif,
        )

        assert not response.text
        assert response.status_code == 201


class TestTagListEndpoint(BaseTestPetstore):

    def test_get_invalid(self, client):
        headers = {
            "Authorization": "Basic testuser",
        }

        response = client.get(
            "/v1/tags",
            headers=headers,
        )

        assert response.status_code == 400
        assert response.json() == {
            "errors": [
                {
                    "title": "Missing response data",
                    "status": 400,
                    "type": "<class 'openapi_core.validation.response.exceptions.MissingData'>",
                },
            ],
        }


class TestSkipResponseTagListEndpoint(BaseTestPetstoreSkipReponse):

    def test_get_valid(self, client):
        headers = {
            "Authorization": "Basic testuser",
        }

        response = client.get(
            "/v1/tags",
            headers=headers,
        )

        assert not response.text
        assert response.status_code == 201
