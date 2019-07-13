import json

import pytest

from openapi_core.schema.media_types.exceptions import InvalidMediaTypeValue
from openapi_core.schema.schemas.enums import UnmarshalContext
from openapi_core.schema.schemas.exceptions import InvalidSchemaProperty
from openapi_core.shortcuts import create_spec
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.wrappers.mock import MockRequest, MockResponse


@pytest.fixture
def response_validator(spec):
    return ResponseValidator(spec)


@pytest.fixture
def request_validator(spec):
    return RequestValidator(spec)


@pytest.fixture('class')
def spec(factory):
    spec_dict = factory.spec_from_file("data/v3.0/read_only_write_only.yaml")
    return create_spec(spec_dict)


class TestWriteOnly(object):

    def test_write_only_property(self, request_validator):
        data = json.dumps({
            'name': "Pedro",
            'hidden': False
        })

        request = MockRequest(host_url='', method='POST',
                              path='/users', data=data)

        is_valid = request_validator.validate(request)
        is_valid.raise_for_errors()
        assert is_valid.body.name == "Pedro"
        assert is_valid.body.hidden is False

    def test_read_a_write_only_property(self, response_validator):
        data = json.dumps({
            'id': 10,
            'name': "Pedro",
            'hidden': True
        })

        request = MockRequest(host_url='', method='POST',
                              path='/users')
        response = MockResponse(data)

        with pytest.raises(InvalidMediaTypeValue) as ex:
            response_validator.validate(request, response).raise_for_errors()
        assert isinstance(ex.value.original_exception, InvalidSchemaProperty)
        ex = ex.value.original_exception

        assert ex.property_name == 'hidden'
        assert UnmarshalContext.RESPONSE.value in str(ex.original_exception)
