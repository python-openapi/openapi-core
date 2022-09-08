from openapi_core.contrib.requests import RequestsOpenAPIResponse


class TestRequestsOpenAPIResponse:
    def test_invalid_server(self, response_factory):
        data = "Not Found"
        status_code = 404
        response = response_factory(data, status_code=status_code)

        openapi_response = RequestsOpenAPIResponse(response)

        assert openapi_response.data == data
        assert openapi_response.status_code == status_code
        mimetype = response.headers.get("Content-Type")
        assert openapi_response.mimetype == mimetype
