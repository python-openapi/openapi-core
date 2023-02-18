from unittest import mock

import pytest
from openapi_schema_validator import OAS31Validator

from openapi_core import RequestValidator
from openapi_core import ResponseValidator
from openapi_core import openapi_request_validator
from openapi_core import openapi_response_validator
from openapi_core.unmarshalling.schemas import oas31_types_unmarshaller
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.schemas import oas31_schema_validators_factory
from openapi_core.validation.schemas.formatters import Formatter


class BaseTestValidate:
    @pytest.fixture
    def schema_unmarshallers_factory(self):
        CUSTOM_FORMATTERS = {"custom": Formatter.from_callables()}
        with pytest.warns(DeprecationWarning):
            return SchemaUnmarshallersFactory(
                oas31_schema_validators_factory,
                oas31_types_unmarshaller,
                custom_formatters=CUSTOM_FORMATTERS,
            )


class TestRequestValidatorValidate(BaseTestValidate):
    @pytest.fixture
    def validator(self, schema_unmarshallers_factory):
        return RequestValidator(schema_unmarshallers_factory)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_valid(self, mock_unmarshal, validator):
        spec = mock.sentinel.spec
        request = mock.sentinel.request

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec, request)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)


class TestResponseValidatorValidate(BaseTestValidate):
    @pytest.fixture
    def validator(self, schema_unmarshallers_factory):
        return ResponseValidator(schema_unmarshallers_factory)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_valid(self, mock_unmarshal, validator):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec, request, response)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)


class TestDetectProxyOpenAPIRequestValidator:
    @pytest.fixture
    def validator(self):
        return openapi_request_validator

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_valid(self, mock_unmarshal, validator, spec_v31):
        request = mock.sentinel.request

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec_v31, request)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)


class TestDetectProxyOpenAPIResponsealidator:
    @pytest.fixture
    def validator(self):
        return openapi_response_validator

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_valid(self, mock_unmarshal, validator, spec_v31):
        request = mock.sentinel.request
        response = mock.sentinel.response

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec_v31, request, response)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)
