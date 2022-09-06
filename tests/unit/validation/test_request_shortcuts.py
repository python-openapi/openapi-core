from unittest import mock

import pytest

from openapi_core.testing.datatypes import ResultMock
from openapi_core.validation.shortcuts import validate_request


class TestValidateRequest:
    @mock.patch(
        "openapi_core.validation.shortcuts.openapi_request_validator.validate"
    )
    def test_validator_valid(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        parameters = mock.sentinel.parameters
        validation_result = ResultMock(parameters=parameters)
        mock_validate.return_value = validation_result

        result = validate_request(spec, request)

        assert result == validation_result
        mock_validate.aasert_called_once_with(request)

    @mock.patch(
        "openapi_core.validation.shortcuts.openapi_request_validator.validate"
    )
    def test_validator_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_request(spec, request)

        mock_validate.aasert_called_once_with(request)
