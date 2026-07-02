import json
from pathlib import Path

from openapi_core import OpenAPI
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse


def test_xquik_search_request_and_response():
    spec_path = Path(__file__).parent / "data/v3.1/xquik-search.yaml"
    openapi = OpenAPI.from_path(spec_path)
    request = MockRequest(
        "https://xquik.com",
        "get",
        "/api/v1/x/tweets/search",
        args={"q": "openapi"},
        headers={"X-API-Key": "test-key"},
    )
    response = MockResponse(
        data=json.dumps(
            {
                "data": [
                    {
                        "id": "1",
                        "text": "OpenAPI",
                        "authorUsername": "xquik",
                    }
                ]
            }
        ).encode("utf-8"),
        status_code=200,
        content_type="application/json",
    )

    request_result = openapi.unmarshal_request(request)
    response_result = openapi.unmarshal_response(request, response)

    assert request_result.errors == []
    assert request_result.parameters.query["q"] == "openapi"
    assert request_result.security == {"apiKey": "test-key"}
    assert response_result.errors == []
    assert response_result.data["data"][0]["authorUsername"] == "xquik"
