from unittest import mock

import pytest

from openapi_core.testing.datatypes import ResultMock
from openapi_core.testing.factories import FactoryClassMock
from openapi_core.validation.response.shortcuts import spec_validate_data


class TestSpecValidateData:
    @mock.patch(
        "openapi_core.validation.response.shortcuts.ResponseDataValidator."
        "validate"
    )
    def test_no_factories(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        data = mock.sentinel.data
        mock_validate.return_value = ResultMock(data=data)

        result = spec_validate_data(spec, request, response)

        assert result == data
        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.shortcuts.ResponseDataValidator."
        "validate"
    )
    def test_no_factories_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            spec_validate_data(spec, request, response)

        mock_validate.aasert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.shortcuts.ResponseDataValidator."
        "validate"
    )
    def test_factories(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        data = mock.sentinel.data
        mock_validate.return_value = ResultMock(data=data)
        request_factory = FactoryClassMock
        response_factory = FactoryClassMock

        result = spec_validate_data(
            spec,
            request,
            response,
            request_factory,
            response_factory,
        )

        assert result == data
        mock_validate.assert_called_once_with(
            FactoryClassMock(request),
            FactoryClassMock(response),
        )

    @mock.patch(
        "openapi_core.validation.response.shortcuts.ResponseDataValidator."
        "validate"
    )
    def test_factories_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        response = mock.sentinel.response
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)
        request_factory = FactoryClassMock
        response_factory = FactoryClassMock

        with pytest.raises(ValueError):
            spec_validate_data(
                spec,
                request,
                response,
                request_factory,
                response_factory,
            )

        mock_validate.assert_called_once_with(
            FactoryClassMock(request),
            FactoryClassMock(response),
        )
