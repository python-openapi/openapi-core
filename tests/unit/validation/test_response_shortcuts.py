from unittest import mock

import pytest

from openapi_core.testing.datatypes import ResultMock
from openapi_core.validation.shortcuts import validate_response


class TestSpecValidateData:
    @mock.patch(
        "openapi_core.validation.shortcuts.openapi_response_validator.validate"
    )
    def test_validator_valid(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        data = mock.sentinel.data
        validation_result = ResultMock(data=data)
        mock_validate.return_value = validation_result

        result = validate_response(request, response, spec=spec)

        assert result == validation_result
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.shortcuts.openapi_response_validator.validate"
    )
    def test_validator_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec)

        mock_validate.aasert_called_once_with(request, response)
