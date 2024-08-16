import json

import pytest
from jsonschema_path import SchemaPath

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core import V30ResponseUnmarshaller
from openapi_core.testing import MockRequest
from openapi_core.testing import MockResponse


class TestParentReference:

    spec_path = "data/v3.0/parent-reference/openapi.yaml"

    @pytest.fixture
    def unmarshaller(self, content_factory):
        content, base_uri = content_factory.from_file(self.spec_path)
        return V30ResponseUnmarshaller(
            spec=SchemaPath.from_dict(content, base_uri=base_uri)
        )

    @pytest.fixture
    def openapi(self, content_factory):
        content, base_uri = content_factory.from_file(self.spec_path)
        spec = SchemaPath.from_dict(content, base_uri=base_uri)
        config = Config(spec_base_uri=base_uri)
        return OpenAPI(spec, config=config)

    def test_valid(self, openapi):
        request = MockRequest(host_url="", method="GET", path="/books")
        response = MockResponse(
            data=json.dumps([{"id": "BOOK:01", "title": "Test Book"}]).encode()
        )

        openapi.validate_response(request, response)

    def test_unmarshal(self, unmarshaller):
        request = MockRequest(host_url="", method="GET", path="/books")
        response = MockResponse(
            data=json.dumps([{"id": "BOOK:01", "title": "Test Book"}]).encode()
        )

        unmarshaller.unmarshal(request, response)
