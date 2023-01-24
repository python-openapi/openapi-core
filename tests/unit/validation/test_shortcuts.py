from unittest import mock

import pytest

from openapi_core import validate_request
from openapi_core import validate_response
from openapi_core.testing.datatypes import ResultMock
from openapi_core.validation.exceptions import ValidatorDetectError
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import WebhookRequest
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.request.validators import WebhookRequestValidator
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.validation.response.validators import (
    WebhookResponseValidator,
)


class TestValidateRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(ValidatorDetectError):
            validate_request(request, spec=spec_invalid)

    def test_request_type_error(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            validate_request(request, spec=spec_v31)

    def test_spec_type_error(self):
        request = mock.Mock(spec=Request)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_request(request, spec=spec)

    @mock.patch(
        "openapi_core.validation.request.validators.RequestValidator.validate",
    )
    def test_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)

        result = validate_request(request, spec=spec_v31)

        assert result == mock_validate.return_value
        mock_validate.validate.aasert_called_once_with(request)

    @mock.patch(
        "openapi_core.validation.request.validators.RequestValidator.validate",
    )
    def test_spec_as_first_arg_deprecated(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.warns(DeprecationWarning):
            result = validate_request(spec_v31, request)

        assert result == mock_validate.return_value
        mock_validate.validate.aasert_called_once_with(request)

    @mock.patch(
        "openapi_core.validation.request.validators.RequestValidator.validate",
    )
    def test_request_error(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_request(request, spec=spec_v31)

        mock_validate.aasert_called_once_with(request)

    def test_validator(self, spec_v31):
        request = mock.Mock(spec=Request)
        validator = mock.Mock(spec=RequestValidator)

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                request, spec=spec_v31, validator=validator
            )

        assert result == validator.validate.return_value
        validator.validate.aasert_called_once_with(request)

    def test_validator_cls(self, spec_v31):
        request = mock.Mock(spec=Request)
        validator_cls = mock.Mock(spec=RequestValidator)

        result = validate_request(request, spec=spec_v31, cls=validator_cls)

        assert result == validator_cls().validate.return_value
        validator_cls().validate.aasert_called_once_with(request)

    @mock.patch(
        "openapi_core.validation.request.validators.WebhookRequestValidator."
        "validate",
    )
    def test_webhook_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        result = validate_request(request, spec=spec_v31)

        assert result == mock_validate.return_value
        mock_validate.validate.aasert_called_once_with(request)

    def test_webhook_request_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(ValidatorDetectError):
            validate_request(request, spec=spec_v30)

    @mock.patch(
        "openapi_core.validation.request.validators.WebhookRequestValidator."
        "validate",
    )
    def test_webhook_request_error(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_request(request, spec=spec_v31)

        mock_validate.aasert_called_once_with(request)

    def test_webhook_validator_cls(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        validator_cls = mock.Mock(spec=WebhookRequestValidator)

        result = validate_request(request, spec=spec_v31, cls=validator_cls)

        assert result == validator_cls().validate.return_value
        validator_cls().validate.aasert_called_once_with(request)


class TestValidateResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(ValidatorDetectError):
            validate_response(request, response, spec=spec_invalid)

    def test_request_type_error(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31)

    def test_response_type_error(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31)

    def test_spec_type_error(self):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec)

    @mock.patch(
        "openapi_core.validation.response.validators.ResponseValidator."
        "validate",
    )
    def test_request_response(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        result = validate_response(request, response, spec=spec_v31)

        assert result == mock_validate.return_value
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.validators.ResponseValidator."
        "validate",
    )
    def test_spec_as_first_arg_deprecated(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        result = validate_response(spec_v31, request, response)

        assert result == mock_validate.return_value
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.validators.ResponseValidator."
        "validate",
    )
    def test_request_response_error(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec_v31)

        mock_validate.aasert_called_once_with(request, response)

    def test_validator(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        validator = mock.Mock(spec=ResponseValidator)

        with pytest.warns(DeprecationWarning):
            result = validate_response(
                request, response, spec=spec_v31, validator=validator
            )

        assert result == validator.validate.return_value
        validator.validate.aasert_called_once_with(request)

    def test_validator_cls(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        validator_cls = mock.Mock(spec=ResponseValidator)

        result = validate_response(
            request, response, spec=spec_v31, cls=validator_cls
        )

        assert result == validator_cls().validate.return_value
        validator_cls().validate.aasert_called_once_with(request)

    def test_webhook_response_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(ValidatorDetectError):
            validate_response(request, response, spec=spec_v30)

    @mock.patch(
        "openapi_core.validation.response.validators.WebhookResponseValidator."
        "validate",
    )
    def test_webhook_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        result = validate_response(request, response, spec=spec_v31)

        assert result == mock_validate.return_value
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.validators.WebhookResponseValidator."
        "validate",
    )
    def test_webhook_request_error(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec_v31)

        mock_validate.aasert_called_once_with(request, response)

    def test_webhook_response_cls(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        validator_cls = mock.Mock(spec=WebhookResponseValidator)

        result = validate_response(
            request, response, spec=spec_v31, cls=validator_cls
        )

        assert result == validator_cls().validate.return_value
        validator_cls().validate.aasert_called_once_with(request)
