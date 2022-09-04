from openapi_core.contrib.flask import FlaskOpenAPIResponse


class TestFlaskOpenAPIResponse:
    def test_invalid_server(self, response_factory):
        response = response_factory("Not Found", status_code=404)

        openapi_response = FlaskOpenAPIResponse(response)

        assert openapi_response.data == response.data
        assert openapi_response.status_code == response._status_code
        assert openapi_response.mimetype == response.mimetype
