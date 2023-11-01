import pytest

from openapi_core.contrib.flask import FlaskOpenAPIResponse


class TestFlaskOpenAPIResponse:
    def test_type_invalid(self):
        with pytest.raises(TypeError):
            FlaskOpenAPIResponse(None)

    def test_invalid_server(self, response_factory):
        data = b"Not Found"
        status_code = 404
        response = response_factory(data, status_code=status_code)

        openapi_response = FlaskOpenAPIResponse(response)

        assert openapi_response.data == data
        assert openapi_response.status_code == status_code
        assert openapi_response.content_type == response.mimetype
