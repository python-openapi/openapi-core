import os
import sys
from base64 import b64encode
from json import dumps
from unittest import mock

import pytest
from django.test.utils import override_settings


class BaseTestDjangoProject:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")

    @pytest.fixture(autouse=True, scope="module")
    def django_setup(self):
        directory = os.path.abspath(os.path.dirname(__file__))
        django_project_dir = os.path.join(directory, "data/v3.0")
        sys.path.insert(0, django_project_dir)
        with mock.patch.dict(
            os.environ,
            {
                "DJANGO_SETTINGS_MODULE": "djangoproject.settings",
            },
        ):
            import django

            django.setup()
            yield
        sys.path.remove(django_project_dir)

    @pytest.fixture
    def client(self):
        from django.test import Client

        return Client()


class TestPetListView(BaseTestDjangoProject):
    def test_get_no_required_param(self, client):
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }

        with pytest.warns(DeprecationWarning):
            response = client.get("/v1/pets", **headers)

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
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }

        with pytest.warns(DeprecationWarning):
            response = client.get("/v1/pets", data_json, **headers)

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
        headers = {
            "HTTP_HOST": "petstore.swagger.io",
        }
        response = client.post("/v1/pets", **headers)

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
        client.cookies.load({"user": 1})
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
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "staging.gigantic-server.com",
        }
        response = client.post(
            "/v1/pets", data_json, content_type, secure=True, **headers
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
        client.cookies.load({"user": 1})
        data = "data"
        content_type = "text/html"
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "staging.gigantic-server.com",
            "HTTP_API_KEY": self.api_key_encoded,
        }
        response = client.post(
            "/v1/pets", data, content_type, secure=True, **headers
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
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "staging.gigantic-server.com",
            "HTTP_API_KEY": self.api_key_encoded,
        }
        response = client.post(
            "/v1/pets", data_json, content_type, secure=True, **headers
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
        client.cookies.load({"user": 1})
        content_type = "application/json"
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "staging.gigantic-server.com",
            "HTTP_API_KEY": self.api_key_encoded,
        }
        response = client.post(
            "/v1/pets", data_json, content_type, secure=True, **headers
        )

        assert response.status_code == 201
        assert not response.content


class TestPetDetailView(BaseTestDjangoProject):
    def test_get_server_invalid(self, client):
        response = client.get("/v1/pets/12")

        expected_data = (
            b"You may need to add &#x27;testserver&#x27; to ALLOWED_HOSTS."
        )
        assert response.status_code == 400
        assert expected_data in response.content

    def test_get_unauthorized(self, client):
        headers = {
            "HTTP_HOST": "petstore.swagger.io",
        }
        response = client.get("/v1/pets/12", **headers)

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
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        response = client.delete("/v1/pets/12", **headers)

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
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        response = client.get("/v1/pets/12", **headers)

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


class BaseTestDRF(BaseTestDjangoProject):
    @pytest.fixture
    def api_client(self):
        from rest_framework.test import APIClient

        return APIClient()


class TestDRFPetListView(BaseTestDRF):
    def test_post_valid(self, api_client):
        api_client.cookies.load({"user": 1})
        content_type = "application/json"
        data_json = {
            "id": 12,
            "name": "Cat",
            "ears": {
                "healthy": True,
            },
        }
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "staging.gigantic-server.com",
            "HTTP_API_KEY": self.api_key_encoded,
        }
        response = api_client.post(
            "/v1/pets",
            dumps(data_json),
            content_type=content_type,
            secure=True,
            **headers,
        )

        assert response.status_code == 201
        assert not response.content


class TestDRFTagListView(BaseTestDRF):
    def test_get_response_invalid(self, client):
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        response = client.get("/v1/tags", **headers)

        assert response.status_code == 415

    def test_get_skip_response_validation(self, client):
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        with override_settings(OPENAPI_RESPONSE_CLS=None):
            response = client.get("/v1/tags", **headers)

        assert response.status_code == 200
        assert response.content == b"success"


class TestPetPhotoView(BaseTestDjangoProject):
    def test_get_valid(self, client, data_gif):
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        response = client.get("/v1/pets/12/photo", **headers)

        assert response.status_code == 200
        assert b"".join(list(response.streaming_content)) == data_gif

    def test_post_valid(self, client, data_gif):
        client.cookies.load({"user": 1})
        content_type = "image/gif"
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
            "HTTP_API_KEY": self.api_key_encoded,
        }
        response = client.post(
            "/v1/pets/12/photo", data_gif, content_type, **headers
        )

        assert response.status_code == 201
        assert not response.content


class TestStatusView(BaseTestDjangoProject):

    def test_get_valid(self, client, data_gif):
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        from django.conf import settings

        MIDDLEWARE = [
            v for v in settings.MIDDLEWARE if "openapi_core" not in v
        ]
        with override_settings(MIDDLEWARE=MIDDLEWARE):
            response = client.get("/status", **headers)

        assert response.status_code == 200
        assert response.content.decode() == "OK"

    def test_post_valid(self, client):
        data = {"key": "value"}
        content_type = "application/json"
        headers = {
            "HTTP_AUTHORIZATION": "Basic testuser",
            "HTTP_HOST": "petstore.swagger.io",
        }
        from django.conf import settings

        MIDDLEWARE = [
            v for v in settings.MIDDLEWARE if "openapi_core" not in v
        ]
        with override_settings(MIDDLEWARE=MIDDLEWARE):
            response = client.post(
                "/status", data=data, content_type=content_type, **headers
            )

        assert response.status_code == 405  # Method Not Allowed
