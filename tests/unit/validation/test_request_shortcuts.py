import mock

import pytest

from openapi_core.testing.datatypes import ResultMock
from openapi_core.testing.factories import FactoryClassMock
from openapi_core.validation.request.shortcuts import (
    spec_validate_parameters, spec_validate_body,
)


class TestSpecValidateParameters(object):

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_no_request_factory(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        parameters = mock.sentinel.parameters
        mock_validate.return_value = ResultMock(parameters=parameters)

        result = spec_validate_parameters(spec, request)

        assert result == parameters
        mock_validate.aasert_called_once_with(request)

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_no_request_factory_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            spec_validate_parameters(spec, request)

        mock_validate.aasert_called_once_with(request)

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_request_factory(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        parameters = mock.sentinel.parameters
        mock_validate.return_value = ResultMock(parameters=parameters)
        request_factory = FactoryClassMock

        result = spec_validate_parameters(spec, request, request_factory)

        assert result == parameters
        mock_validate.assert_called_once_with(
            FactoryClassMock(request),
        )

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_request_factory_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)
        request_factory = FactoryClassMock

        with pytest.raises(ValueError):
            spec_validate_parameters(spec, request, request_factory)

        mock_validate.assert_called_once_with(
            FactoryClassMock(request),
        )


class TestSpecValidateBody(object):

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_no_request_factory(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        body = mock.sentinel.body
        mock_validate.return_value = ResultMock(body=body)

        result = spec_validate_body(spec, request)

        assert result == body
        mock_validate.aasert_called_once_with(request)

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_no_request_factory_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            spec_validate_body(spec, request)

        mock_validate.aasert_called_once_with(request)

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_request_factory(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        body = mock.sentinel.body
        mock_validate.return_value = ResultMock(body=body)
        request_factory = FactoryClassMock

        result = spec_validate_body(spec, request, request_factory)

        assert result == body
        mock_validate.assert_called_once_with(
            FactoryClassMock(request),
        )

    @mock.patch(
        'openapi_core.validation.request.shortcuts.RequestValidator.validate'
    )
    def test_request_factory_error(self, mock_validate):
        spec = mock.sentinel.spec
        request = mock.sentinel.request
        mock_validate.return_value = ResultMock(error_to_raise=ValueError)
        request_factory = FactoryClassMock

        with pytest.raises(ValueError):
            spec_validate_body(spec, request, request_factory)

        mock_validate.assert_called_once_with(
            FactoryClassMock(request),
        )
