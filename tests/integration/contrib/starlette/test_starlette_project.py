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


@pytest.fixture
def app():
    from starletteproject.__main__ import app

    return app


@pytest.fixture
def client(app):
    return TestClient(app, base_url="http://petstore.swagger.io")


class BaseTestPetstore:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class TestPetPhotoView(BaseTestPetstore):
    @pytest.mark.xfail(
        reason="response binary format not supported",
        strict=True,
    )
    def test_get_valid(self, client, data_gif):
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
        }

        cookies = {"user": "1"}
        response = client.get(
            "/v1/pets/1/photo",
            headers=headers,
            cookies=cookies,
        )

        assert response.get_data() == data_gif
        assert response.status_code == 200

    @pytest.mark.xfail(
        reason="request binary format not supported",
        strict=True,
    )
    def test_post_valid(self, client, data_gif):
        content_type = "image/gif"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
        }

        cookies = {"user": "1"}
        response = client.post(
            "/v1/pets/1/photo",
            headers=headers,
            data=data_gif,
            cookies=cookies,
        )

        assert not response.text
        assert response.status_code == 201
