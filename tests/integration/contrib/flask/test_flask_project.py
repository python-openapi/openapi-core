import os
import sys
from base64 import b64encode

import pytest


@pytest.fixture(autouse=True, scope="module")
def flask_setup():
    directory = os.path.abspath(os.path.dirname(__file__))
    flask_project_dir = os.path.join(directory, "data/v3.0")
    sys.path.insert(0, flask_project_dir)
    yield
    sys.path.remove(flask_project_dir)


@pytest.fixture
def app():
    from flaskproject.__main__ import app

    app.config["SERVER_NAME"] = "petstore.swagger.io"
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    return app


@pytest.fixture
def client(app):
    return app.test_client()


class BaseTestFlaskProject:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class TestPetPhotoView(BaseTestFlaskProject):
    def test_get_valid(self, client, data_gif):
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
        }

        client.set_cookie("user", "1", domain="petstore.swagger.io")
        response = client.get(
            "/v1/pets/1/photo",
            headers=headers,
        )

        assert response.get_data() == data_gif
        assert response.status_code == 200

    def test_post_valid(self, client, data_gif):
        content_type = "image/gif"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }

        client.set_cookie("user", "1", domain="petstore.swagger.io")
        response = client.post(
            "/v1/pets/1/photo",
            headers=headers,
            data=data_gif,
        )

        assert not response.text
        assert response.status_code == 201
