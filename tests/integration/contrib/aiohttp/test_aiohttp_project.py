import os
import sys
from base64 import b64encode
from io import BytesIO

import pytest


@pytest.fixture(autouse=True, scope="session")
def project_setup():
    directory = os.path.abspath(os.path.dirname(__file__))
    project_dir = os.path.join(directory, "data/v3.0")
    sys.path.insert(0, project_dir)
    yield
    sys.path.remove(project_dir)


@pytest.fixture
def app(project_setup):
    from aiohttpproject.__main__ import get_app

    return get_app()


@pytest.fixture
async def client(app, aiohttp_client):
    return await aiohttp_client(app)


class BaseTestPetstore:
    api_key = "12345"

    @property
    def api_key_encoded(self):
        api_key_bytes = self.api_key.encode("utf8")
        api_key_bytes_enc = b64encode(api_key_bytes)
        return str(api_key_bytes_enc, "utf8")


class TestPetPhotoView(BaseTestPetstore):
    async def test_get_valid(self, client, data_gif):
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Host": "petstore.swagger.io",
        }

        cookies = {"user": "1"}
        response = await client.get(
            "/v1/pets/1/photo",
            headers=headers,
            cookies=cookies,
        )

        assert await response.content.read() == data_gif
        assert response.status == 200

    async def test_post_valid(self, client, data_gif):
        content_type = "image/gif"
        headers = {
            "Authorization": "Basic testuser",
            "Api-Key": self.api_key_encoded,
            "Content-Type": content_type,
            "Host": "petstore.swagger.io",
        }
        data = {
            "file": BytesIO(data_gif),
        }

        cookies = {"user": "1"}
        response = await client.post(
            "/v1/pets/1/photo",
            headers=headers,
            data=data,
            cookies=cookies,
        )

        assert not await response.text()
        assert response.status == 201
