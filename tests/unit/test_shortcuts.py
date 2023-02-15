from unittest import mock

import pytest

from openapi_core import RequestValidator
from openapi_core import ResponseValidator
from openapi_core import unmarshal_request
from openapi_core import unmarshal_response
from openapi_core import unmarshal_webhook_request
from openapi_core import unmarshal_webhook_response
from openapi_core import validate_request
from openapi_core import validate_response
from openapi_core.exceptions import SpecError
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.testing.datatypes import ResultMock
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.unmarshallers import (
    APICallRequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    WebhookRequestUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    APICallResponseUnmarshaller,
)


class MockClass:
    schema_validators_factory = None
    schema_unmarshallers_factory = None

    unmarshal_calls = []
    return_unmarshal = None

    @classmethod
    def setUp(cls, return_unmarshal):
        cls.unmarshal_calls = []
        cls.return_unmarshal = return_unmarshal


class MockReqClass(MockClass):
    assert_request = None

    @classmethod
    def setUp(cls, return_unmarshal, assert_request):
        super().setUp(return_unmarshal)
        cls.assert_request = assert_request

    def unmarshal(self, req):
        self.unmarshal_calls.append([req])
        assert req == self.assert_request
        return self.return_unmarshal


class MockRespClass(MockClass):
    assert_request = None
    assert_response = None

    @classmethod
    def setUp(cls, return_unmarshal, assert_request, assert_response):
        super().setUp(return_unmarshal)
        cls.assert_request = assert_request
        cls.assert_response = assert_response

    def unmarshal(self, req, resp):
        self.unmarshal_calls.append([req, resp])
        assert req == self.assert_request
        assert resp == self.assert_response
        return self.return_unmarshal


class TestUnmarshalRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            unmarshal_request(request, spec=spec_invalid)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            unmarshal_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_request(request, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.raises(TypeError):
            unmarshal_request(request, spec=spec_v31, cls=Exception)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_request(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)

        result = unmarshal_request(request, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)


class TestUnmarshalWebhookRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            unmarshal_webhook_request(request, spec=spec_invalid)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            unmarshal_webhook_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=WebhookRequest)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_webhook_request(request, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(TypeError):
            unmarshal_webhook_request(request, spec=spec_v31, cls=Exception)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.WebhookRequestUnmarshaller."
        "unmarshal",
    )
    def test_request(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        result = unmarshal_webhook_request(request, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)


class TestUnmarshalResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_response(request, response, spec=spec_invalid)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            unmarshal_response(request, response, spec=spec_v31)

    def test_response_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            unmarshal_response(request, response, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_response(request, response, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            unmarshal_response(request, response, spec=spec_v31, cls=Exception)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_request_response(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        result = unmarshal_response(request, response, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)


class TestUnmarshalWebhookResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_webhook_response(request, response, spec=spec_invalid)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            unmarshal_webhook_response(request, response, spec=spec_v31)

    def test_response_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            unmarshal_webhook_response(request, response, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_webhook_response(request, response, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            unmarshal_webhook_response(
                request, response, spec=spec_v31, cls=Exception
            )

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.WebhookResponseUnmarshaller."
        "unmarshal",
    )
    def test_request_response(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        result = unmarshal_webhook_response(request, response, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)


class TestValidateRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            validate_request(request, spec=spec_invalid)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            validate_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_request(request, spec=spec)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_request(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)

        result = validate_request(request, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_spec_as_first_arg_deprecated(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.warns(DeprecationWarning):
            result = validate_request(spec_v31, request)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_request_error(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        mock_unmarshal.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_request(request, spec=spec_v31)

        mock_unmarshal.assert_called_once_with(request)

    def test_validator(self, spec_v31):
        request = mock.Mock(spec=Request)
        validator = mock.Mock(spec=RequestValidator)

        with pytest.warns(DeprecationWarning):
            result = validate_request(
                request, spec=spec_v31, validator=validator
            )

        assert result == validator.validate.return_value
        validator.validate.assert_called_once_with(
            spec_v31, request, base_url=None
        )

    def test_cls(self, spec_v31):
        request = mock.Mock(spec=Request)
        unmarshal = mock.Mock(spec=RequestUnmarshalResult)
        TestAPICallReq = type(
            "TestAPICallReq",
            (MockReqClass, APICallRequestUnmarshaller),
            {},
        )
        TestAPICallReq.setUp(unmarshal, request)

        result = validate_request(request, spec=spec_v31, cls=TestAPICallReq)

        assert result == unmarshal
        assert len(TestAPICallReq.unmarshal_calls) == 1

    def test_cls_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.raises(TypeError):
            validate_request(request, spec=spec_v31, cls=Exception)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.WebhookRequestUnmarshaller."
        "unmarshal",
    )
    def test_webhook_request(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        result = validate_request(request, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)

    def test_webhook_request_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            validate_request(request, spec=spec_v30)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.WebhookRequestUnmarshaller."
        "unmarshal",
    )
    def test_webhook_request_error(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        mock_unmarshal.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_request(request, spec=spec_v31)

        mock_unmarshal.assert_called_once_with(request)

    def test_webhook_cls(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        unmarshal = mock.Mock(spec=RequestUnmarshalResult)
        TestWebhookReq = type(
            "TestWebhookReq",
            (MockReqClass, WebhookRequestUnmarshaller),
            {},
        )
        TestWebhookReq.setUp(unmarshal, request)

        result = validate_request(request, spec=spec_v31, cls=TestWebhookReq)

        assert result == unmarshal
        assert len(TestWebhookReq.unmarshal_calls) == 1

    def test_webhook_cls_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(TypeError):
            validate_request(request, spec=spec_v31, cls=Exception)


class TestValidateResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_response(request, response, spec=spec_invalid)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31)

    def test_response_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_request_response(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        result = validate_response(request, response, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_spec_as_first_arg_deprecated(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.warns(DeprecationWarning):
            result = validate_response(spec_v31, request, response)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_request_response_error(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        mock_unmarshal.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec_v31)

        mock_unmarshal.assert_called_once_with(request, response)

    def test_validator(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        validator = mock.Mock(spec=ResponseValidator)

        with pytest.warns(DeprecationWarning):
            result = validate_response(
                request, response, spec=spec_v31, validator=validator
            )

        assert result == validator.validate.return_value
        validator.validate.assert_called_once_with(
            spec_v31, request, response, base_url=None
        )

    def test_cls(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        unmarshal = mock.Mock(spec=RequestUnmarshalResult)
        TestAPICallResp = type(
            "TestAPICallResp",
            (MockRespClass, APICallResponseUnmarshaller),
            {},
        )
        TestAPICallResp.setUp(unmarshal, request, response)

        result = validate_response(
            request, response, spec=spec_v31, cls=TestAPICallResp
        )

        assert result == unmarshal
        assert len(TestAPICallResp.unmarshal_calls) == 1

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31, cls=Exception)

    def test_webhook_response_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_response(request, response, spec=spec_v30)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.WebhookResponseUnmarshaller."
        "unmarshal",
    )
    def test_webhook_request(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        result = validate_response(request, response, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.WebhookResponseUnmarshaller."
        "unmarshal",
    )
    def test_webhook_request_error(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        mock_unmarshal.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec_v31)

        mock_unmarshal.assert_called_once_with(request, response)

    def test_webhook_cls(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        unmarshal = mock.Mock(spec=RequestUnmarshalResult)
        TestWebhookResp = type(
            "TestWebhookResp",
            (MockRespClass, APICallResponseUnmarshaller),
            {},
        )
        TestWebhookResp.setUp(unmarshal, request, response)

        result = validate_response(
            request, response, spec=spec_v31, cls=TestWebhookResp
        )

        assert result == unmarshal
        assert len(TestWebhookResp.unmarshal_calls) == 1

    def test_webhook_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31, cls=Exception)
