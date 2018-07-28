import json
import pytest

from openapi_core.extensions.models.models import BaseModel
from openapi_core.schema.media_types.exceptions import (
    InvalidContentType, InvalidMediaTypeValue,
)
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.parameters.exceptions import MissingRequiredParameter
from openapi_core.schema.request_bodies.exceptions import MissingRequestBody
from openapi_core.schema.responses.exceptions import (
    MissingResponseContent, InvalidResponse,
)
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.wrappers.mock import MockRequest, MockResponse


class TestModelsExtension(object):

    host_url = 'http://petstore.swagger.io'

    @pytest.fixture
    def spec_dict(self, factory):
        return factory.spec_from_file("data/v3.0/petstore.yaml")

    @pytest.fixture
    def spec(self, spec_dict):
        return create_spec(spec_dict)

    @pytest.fixture
    def validator(self, spec):
        return ResponseValidator(spec)

    def test_get_pets(self, validator):
        request = MockRequest(self.host_url, 'get', '/v1/pets')
        response_json = {
            'data': [
                {
                    'id': 1,
                    'name': 'Sparky'
                },
            ],
        }
        response_data = json.dumps(response_json)
        response = MockResponse(response_data)

        result = validator.validate(request, response)

        assert result.errors == []
        assert list(result.data.keys()) == ['data', ]
        assert len(result.data['data']) == 1
        assert isinstance(result.data['data'][0], BaseModel)
        assert result.data['data'][0].id == 1
        assert result.data['data'][0].name == 'Sparky'
