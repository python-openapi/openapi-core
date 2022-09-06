from unittest import mock

import pytest

from openapi_core.testing.datatypes import ResultMock
from openapi_core.validation.response.shortcuts import spec_validate_response


class TestSpecValidateData:
    @mock.patch(
        "openapi_core.validation.response.shortcuts.ResponseValidator.validate"
    )
    def test_validator_valid(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        data = mock.sentinel.data
        validation_result = ResultMock(data=data)
        mock_validate.return_value = validation_result

        result = spec_validate_response(spec, request, response)

        assert result == validation_result
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.shortcuts.ResponseValidator.validate"
    )
    def test_validator_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            spec_validate_response(spec, request, response)

        mock_validate.aasert_called_once_with(request, response)
