from unittest import mock

import pytest
from openapi_schema_validator import OAS31Validator

from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.validation import openapi_request_validator
from openapi_core.validation import openapi_response_validator
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class BaseTestValidate:
    @pytest.fixture
    def schema_unmarshallers_factory(self):
        CUSTOM_FORMATTERS = {"custom": Formatter.from_callables()}
        return SchemaUnmarshallersFactory(
            OAS31Validator,
            custom_formatters=CUSTOM_FORMATTERS,
        )


class TestRequestValidatorValidate(BaseTestValidate):
    @pytest.fixture
    def validator(self, schema_unmarshallers_factory):
        return RequestValidator(schema_unmarshallers_factory)

    @mock.patch(
        "openapi_core.validation.request.validators.APICallRequestValidator."
        "validate",
    )
    def test_valid(self, mock_validate, validator):
        spec = mock.sentinel.spec
        request = mock.sentinel.request

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec, request)

        assert result == mock_validate.return_value
        mock_validate.assert_called_once_with(request)


class TestResponseValidatorValidate(BaseTestValidate):
    @pytest.fixture
    def validator(self, schema_unmarshallers_factory):
        return ResponseValidator(schema_unmarshallers_factory)

    @mock.patch(
        "openapi_core.validation.response.validators.APICallResponseValidator."
        "validate",
    )
    def test_valid(self, mock_validate, validator):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec, request, response)

        assert result == mock_validate.return_value
        mock_validate.assert_called_once_with(request, response)


class TestDetectProxyOpenAPIRequestValidator:
    @pytest.fixture
    def validator(self):
        return openapi_request_validator

    @mock.patch(
        "openapi_core.validation.request.validators.APICallRequestValidator."
        "validate",
    )
    def test_valid(self, mock_validate, validator, spec_v31):
        request = mock.sentinel.request

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec_v31, request)

        assert result == mock_validate.return_value
        mock_validate.assert_called_once_with(request)


class TestDetectProxyOpenAPIResponsealidator:
    @pytest.fixture
    def validator(self):
        return openapi_response_validator

    @mock.patch(
        "openapi_core.validation.response.validators.APICallResponseValidator."
        "validate",
    )
    def test_valid(self, mock_validate, validator, spec_v31):
        request = mock.sentinel.request
        response = mock.sentinel.response

        with pytest.warns(DeprecationWarning):
            result = validator.validate(spec_v31, request, response)

        assert result == mock_validate.return_value
        mock_validate.assert_called_once_with(request, response)
