from openapi_core.contrib.requests import RequestsOpenAPIResponse


class TestRequestsOpenAPIResponse:

    def test_invalid_server(self, response_factory):
        response = response_factory('Not Found', status_code=404)

        openapi_response = RequestsOpenAPIResponse(response)

        assert openapi_response.data == response.content
        assert openapi_response.status_code == response.status_code
        mimetype = response.headers.get('Content-Type')
        assert openapi_response.mimetype == mimetype
