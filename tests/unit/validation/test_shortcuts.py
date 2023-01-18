from unittest import mock

import pytest

from openapi_core import validate_request
from openapi_core import validate_response
from openapi_core.testing.datatypes import ResultMock
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestValidateRequest:
    @mock.patch(
        "openapi_core.validation.request.validators.RequestValidator.validate",
    )
    def test_valid(self, mock_validate):
        spec = {"openapi": "3.1"}
        request = mock.sentinel.request

        result = validate_request(request, spec=spec)

        assert result == mock_validate.return_value
        mock_validate.validate.aasert_called_once_with(request)

    @mock.patch(
        "openapi_core.validation.request.validators.RequestValidator.validate",
    )
    def test_error(self, mock_validate):
        spec = {"openapi": "3.1"}
        request = mock.sentinel.request
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_request(request, spec=spec)

        mock_validate.aasert_called_once_with(request)

    def test_validator(self):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        validator = mock.Mock(spec=RequestValidator)

        with pytest.warns(DeprecationWarning):
            result = validate_request(request, spec=spec, validator=validator)

        assert result == validator.validate.return_value
        validator.validate.aasert_called_once_with(request)

    def test_cls(self):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        validator_cls = mock.Mock(spec=RequestValidator)

        result = validate_request(request, spec=spec, cls=validator_cls)

        assert result == validator_cls().validate.return_value
        validator_cls().validate.aasert_called_once_with(request)


class TestSpecValidateData:
    @mock.patch(
        "openapi_core.validation.response.validators.ResponseValidator.validate",
    )
    def test_valid(self, mock_validate):
        spec = {"openapi": "3.1"}
        request = mock.sentinel.request
        response = mock.sentinel.response

        result = validate_response(request, response, spec=spec)

        assert result == mock_validate.return_value
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.validators.ResponseValidator.validate",
    )
    def test_error(self, mock_validate):
        spec = {"openapi": "3.1"}
        request = mock.sentinel.request
        response = mock.sentinel.response
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec)

        mock_validate.aasert_called_once_with(request, response)

    def test_validator(self):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        validator = mock.Mock(spec=ResponseValidator)

        with pytest.warns(DeprecationWarning):
            result = validate_response(
                request, response, spec=spec, validator=validator
            )

        assert result == validator.validate.return_value
        validator.validate.aasert_called_once_with(request)

    def test_cls(self):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        validator_cls = mock.Mock(spec=ResponseValidator)

        result = validate_response(
            request, response, spec=spec, cls=validator_cls
        )

        assert result == validator_cls().validate.return_value
        validator_cls().validate.aasert_called_once_with(request)
