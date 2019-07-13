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


class TestReadOnly(object):

    def test_write_a_read_only_property(self, request_validator):
        data = json.dumps({
            'id': 10,
            'name': "Pedro"
        })

        request = MockRequest(host_url='', method='POST',
                              path='/users', data=data)

        with pytest.raises(InvalidMediaTypeValue) as ex:
            request_validator.validate(request).raise_for_errors()
        assert isinstance(ex.value.original_exception, InvalidSchemaProperty)
        ex = ex.value.original_exception

        assert ex.property_name == 'id'
        assert UnmarshalContext.REQUEST.value in str(ex.original_exception)

    def test_read_only_property_response(self, response_validator):
        data = json.dumps({
            'id': 10,
            'name': "Pedro"
        })

        request = MockRequest(host_url='', method='POST',
                              path='/users')

        response = MockResponse(data)

        is_valid = response_validator.validate(request, response)
        is_valid.raise_for_errors()

        assert len(is_valid.errors) == 0
        assert is_valid.data.id == 10
        assert is_valid.data.name == "Pedro"
