from unittest import mock

import pytest
from openapi_spec_validator import OpenAPIV31SpecValidator

from openapi_core import unmarshal_apicall_request
from openapi_core import unmarshal_apicall_response
from openapi_core import unmarshal_request
from openapi_core import unmarshal_response
from openapi_core import unmarshal_webhook_request
from openapi_core import unmarshal_webhook_response
from openapi_core import validate_apicall_request
from openapi_core import validate_apicall_response
from openapi_core import validate_request
from openapi_core import validate_response
from openapi_core import validate_webhook_request
from openapi_core import validate_webhook_response
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
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    APICallResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    WebhookResponseUnmarshaller,
)
from openapi_core.validation.request.validators import APICallRequestValidator
from openapi_core.validation.request.validators import WebhookRequestValidator
from openapi_core.validation.response.validators import (
    APICallResponseValidator,
)
from openapi_core.validation.response.validators import (
    WebhookResponseValidator,
)


class MockClass:
    spec_validator_cls = None
    schema_casters_factory = None
    schema_validators_factory = None
    schema_unmarshallers_factory = None

    unmarshal_calls = []
    validate_calls = []
    return_unmarshal = None

    @classmethod
    def setUp(cls, return_unmarshal=None):
        cls.unmarshal_calls = []
        cls.validate_calls = []
        cls.return_unmarshal = return_unmarshal


class MockReqValidator(MockClass):
    def validate(self, req):
        self.validate_calls.append((req,))


class MockReqUnmarshaller(MockClass):
    def unmarshal(self, req):
        self.unmarshal_calls.append((req,))
        return self.return_unmarshal


class MockRespValidator(MockClass):
    def validate(self, req, resp):
        self.validate_calls.append((req, resp))


class MockRespUnmarshaller(MockClass):
    def unmarshal(self, req, resp):
        self.unmarshal_calls.append((req, resp))
        return self.return_unmarshal


@pytest.fixture(autouse=True)
def setup():
    MockClass.setUp()
    yield


class TestUnmarshalAPICallRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            unmarshal_apicall_request(request, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            unmarshal_apicall_request(request, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            unmarshal_apicall_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_apicall_request(request, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.raises(TypeError):
            unmarshal_apicall_request(request, spec=spec_v31, cls=Exception)


class TestUnmarshalWebhookRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            unmarshal_webhook_request(request, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            unmarshal_webhook_request(request, spec=spec_v20)

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

    def test_spec_oas30_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            unmarshal_webhook_request(request, spec=spec_v30)

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.WebhookRequestUnmarshaller."
        "unmarshal",
    )
    def test_request(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        result = unmarshal_webhook_request(request, spec=spec_v31)

        assert result == mock_unmarshal.return_value
        mock_unmarshal.assert_called_once_with(request)


class TestUnmarshalRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            unmarshal_request(request, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            unmarshal_request(request, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            unmarshal_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_request(request, spec=spec)

    def test_cls_apicall_unmarshaller(self, spec_v31):
        request = mock.Mock(spec=Request)
        unmarshal = mock.Mock(spec=RequestUnmarshalResult)
        TestAPICallReq = type(
            "TestAPICallReq",
            (MockReqUnmarshaller, APICallRequestUnmarshaller),
            {},
        )
        TestAPICallReq.setUp(unmarshal)

        result = unmarshal_request(request, spec=spec_v31, cls=TestAPICallReq)

        assert result == unmarshal
        assert TestAPICallReq.unmarshal_calls == [
            (request,),
        ]

    def test_cls_webhook_unmarshaller(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        unmarshal = mock.Mock(spec=RequestUnmarshalResult)
        TestWebhookReq = type(
            "TestWebhookReq",
            (MockReqUnmarshaller, WebhookRequestUnmarshaller),
            {},
        )
        TestWebhookReq.setUp(unmarshal)

        result = unmarshal_request(request, spec=spec_v31, cls=TestWebhookReq)

        assert result == unmarshal
        assert TestWebhookReq.unmarshal_calls == [
            (request,),
        ]

    @pytest.mark.parametrize("req", [Request, WebhookRequest])
    def test_cls_type_invalid(self, spec_v31, req):
        request = mock.Mock(spec=req)

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

    @mock.patch(
        "openapi_core.unmarshalling.request.unmarshallers.APICallRequestUnmarshaller."
        "unmarshal",
    )
    def test_request_error(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        mock_unmarshal.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            unmarshal_request(request, spec=spec_v31)

        mock_unmarshal.assert_called_once_with(request)


class TestUnmarshalAPICallResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_apicall_response(request, response, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_apicall_response(request, response, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            unmarshal_apicall_response(request, response, spec=spec_v31)

    def test_response_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            unmarshal_apicall_response(request, response, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            unmarshal_apicall_response(request, response, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            unmarshal_apicall_response(
                request, response, spec=spec_v31, cls=Exception
            )


class TestUnmarshalResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_response(request, response, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_response(request, response, spec=spec_v20)

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

    def test_cls_apicall_unmarshaller(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        unmarshal = mock.Mock(spec=ResponseUnmarshalResult)
        TestAPICallReq = type(
            "TestAPICallReq",
            (MockRespUnmarshaller, APICallResponseUnmarshaller),
            {},
        )
        TestAPICallReq.setUp(unmarshal)

        result = unmarshal_response(
            request, response, spec=spec_v31, cls=TestAPICallReq
        )

        assert result == unmarshal
        assert TestAPICallReq.unmarshal_calls == [
            (request, response),
        ]

    def test_cls_webhook_unmarshaller(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        unmarshal = mock.Mock(spec=ResponseUnmarshalResult)
        TestWebhookReq = type(
            "TestWebhookReq",
            (MockRespUnmarshaller, WebhookResponseUnmarshaller),
            {},
        )
        TestWebhookReq.setUp(unmarshal)

        result = unmarshal_response(
            request, response, spec=spec_v31, cls=TestWebhookReq
        )

        assert result == unmarshal
        assert TestWebhookReq.unmarshal_calls == [
            (request, response),
        ]

    @pytest.mark.parametrize("req", [Request, WebhookRequest])
    def test_cls_type_invalid(self, spec_v31, req):
        request = mock.Mock(spec=req)
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

    @mock.patch(
        "openapi_core.unmarshalling.response.unmarshallers.APICallResponseUnmarshaller."
        "unmarshal",
    )
    def test_request_response_error(self, mock_unmarshal, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        mock_unmarshal.return_value = ResultMock(error_to_raise=ValueError)

        with pytest.raises(ValueError):
            unmarshal_response(request, response, spec=spec_v31)

        mock_unmarshal.assert_called_once_with(request, response)


class TestUnmarshalWebhookResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_webhook_response(request, response, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_webhook_response(request, response, spec=spec_v20)

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

    def test_spec_oas30_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            unmarshal_webhook_response(request, response, spec=spec_v30)

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


class TestValidateAPICallRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            validate_apicall_request(request, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            validate_apicall_request(request, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            validate_apicall_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_apicall_request(request, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.raises(TypeError):
            validate_apicall_request(request, spec=spec_v31, cls=Exception)

    @mock.patch(
        "openapi_core.validation.request.validators.APICallRequestValidator."
        "validate",
    )
    def test_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)

        result = validate_apicall_request(request, spec=spec_v31)

        assert result is None
        mock_validate.assert_called_once_with(request)


class TestValidateWebhookRequest:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            validate_webhook_request(request, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            validate_webhook_request(request, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request

        with pytest.raises(TypeError):
            validate_webhook_request(request, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=WebhookRequest)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_webhook_request(request, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(TypeError):
            validate_webhook_request(request, spec=spec_v31, cls=Exception)

    def test_spec_oas30_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            validate_webhook_request(request, spec=spec_v30)

    @mock.patch(
        "openapi_core.validation.request.validators.WebhookRequestValidator."
        "validate",
    )
    def test_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        result = validate_webhook_request(request, spec=spec_v31)

        assert result is None
        mock_validate.assert_called_once_with(request)


class TestValidateRequest:
    def test_spec_invalid(self, spec_invalid):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            validate_request(request, spec=spec_invalid)

    def test_spec_not_detected(self, spec_v20):
        request = mock.Mock(spec=Request)

        with pytest.raises(SpecError):
            validate_request(request, spec=spec_v20)

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
        "openapi_core.validation.request.validators.APICallRequestValidator."
        "validate",
    )
    def test_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        mock_validate.return_value = None

        validate_request(request, spec=spec_v31)

        mock_validate.assert_called_once_with(request)

    def test_cls_apicall(self, spec_v31):
        request = mock.Mock(spec=Request)
        TestAPICallReq = type(
            "TestAPICallReq",
            (MockReqValidator, APICallRequestValidator),
            {},
        )

        result = validate_request(request, spec=spec_v31, cls=TestAPICallReq)

        assert result is None
        assert TestAPICallReq.validate_calls == [
            (request,),
        ]

    def test_cls_apicall_with_spec_validator_cls(self, spec_v31):
        request = mock.Mock(spec=Request)
        TestAPICallReq = type(
            "TestAPICallReq",
            (MockReqValidator, APICallRequestValidator),
            {
                "spec_validator_cls": OpenAPIV31SpecValidator,
            },
        )

        result = validate_request(request, spec=spec_v31, cls=TestAPICallReq)

        assert result is None
        assert TestAPICallReq.validate_calls == [
            (request,),
        ]

    def test_cls_webhook(self, spec_v31):
        request = mock.Mock(spec=Request)
        TestWebhookReq = type(
            "TestWebhookReq",
            (MockReqValidator, WebhookRequestValidator),
            {},
        )

        result = validate_request(request, spec=spec_v31, cls=TestWebhookReq)

        assert result is None
        assert TestWebhookReq.validate_calls == [
            (request,),
        ]

    def test_cls_webhook_with_spec_validator_cls(self, spec_v31):
        request = mock.Mock(spec=Request)
        TestWebhookReq = type(
            "TestWebhookReq",
            (MockReqValidator, WebhookRequestValidator),
            {
                "spec_validator_cls": OpenAPIV31SpecValidator,
            },
        )

        result = validate_request(request, spec=spec_v31, cls=TestWebhookReq)

        assert result is None
        assert TestWebhookReq.validate_calls == [
            (request,),
        ]

    def test_webhook_cls(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        TestWebhookReq = type(
            "TestWebhookReq",
            (MockReqValidator, WebhookRequestValidator),
            {},
        )

        result = validate_request(request, spec=spec_v31, cls=TestWebhookReq)

        assert result is None
        assert TestWebhookReq.validate_calls == [
            (request,),
        ]

    def test_cls_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)

        with pytest.raises(TypeError):
            validate_request(request, spec=spec_v31, cls=Exception)

    @mock.patch(
        "openapi_core.validation.request.validators.V31WebhookRequestValidator."
        "validate",
    )
    def test_webhook_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        mock_validate.return_value = None

        validate_request(request, spec=spec_v31)

        mock_validate.assert_called_once_with(request)

    def test_webhook_request_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(SpecError):
            validate_request(request, spec=spec_v30)

    @mock.patch(
        "openapi_core.validation.request.validators.V31WebhookRequestValidator."
        "validate",
    )
    def test_webhook_request_error(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        mock_validate.side_effect = ValueError

        with pytest.raises(ValueError):
            validate_request(request, spec=spec_v31)

        mock_validate.assert_called_once_with(request)

    def test_webhook_cls_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)

        with pytest.raises(TypeError):
            validate_request(request, spec=spec_v31, cls=Exception)


class TestValidateAPICallResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_apicall_response(request, response, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_apicall_response(request, response, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_apicall_response(request, response, spec=spec_v31)

    def test_response_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            validate_apicall_response(request, response, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_apicall_response(request, response, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_apicall_response(
                request, response, spec=spec_v31, cls=Exception
            )

    @mock.patch(
        "openapi_core.validation.response.validators.APICallResponseValidator."
        "validate",
    )
    def test_request_response(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        result = validate_apicall_response(request, response, spec=spec_v31)

        assert result is None
        mock_validate.assert_called_once_with(request, response)


class TestValidateWebhookResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_webhook_response(request, response, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_webhook_response(request, response, spec=spec_v20)

    def test_request_type_invalid(self, spec_v31):
        request = mock.sentinel.request
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_webhook_response(request, response, spec=spec_v31)

    def test_response_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.sentinel.response

        with pytest.raises(TypeError):
            validate_webhook_response(request, response, spec=spec_v31)

    def test_spec_type_invalid(self):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        spec = mock.sentinel.spec

        with pytest.raises(TypeError):
            validate_webhook_response(request, response, spec=spec)

    def test_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_webhook_response(
                request, response, spec=spec_v31, cls=Exception
            )

    def test_spec_oas30_validator_not_found(self, spec_v30):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_webhook_response(request, response, spec=spec_v30)

    @mock.patch(
        "openapi_core.validation.response.validators.WebhookResponseValidator."
        "validate",
    )
    def test_request_response(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        result = validate_webhook_response(request, response, spec=spec_v31)

        assert result is None
        mock_validate.assert_called_once_with(request, response)


class TestValidateResponse:
    def test_spec_not_detected(self, spec_invalid):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_response(request, response, spec=spec_invalid)

    def test_spec_not_supported(self, spec_v20):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)

        with pytest.raises(SpecError):
            validate_response(request, response, spec=spec_v20)

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
        "openapi_core.validation.response.validators.APICallResponseValidator."
        "validate",
    )
    def test_request_response(self, mock_validate, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        mock_validate.return_value = None

        validate_response(request, response, spec=spec_v31)

        mock_validate.assert_called_once_with(request, response)

    def test_cls_apicall(self, spec_v31):
        request = mock.Mock(spec=Request)
        response = mock.Mock(spec=Response)
        TestAPICallResp = type(
            "TestAPICallResp",
            (MockRespValidator, APICallResponseValidator),
            {},
        )

        result = validate_response(
            request, response, spec=spec_v31, cls=TestAPICallResp
        )

        assert result is None
        assert TestAPICallResp.validate_calls == [
            (request, response),
        ]

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
        "openapi_core.validation.response.validators.V31WebhookResponseValidator."
        "validate",
    )
    def test_webhook_request(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        mock_validate.return_value = None

        validate_response(request, response, spec=spec_v31)

        mock_validate.assert_called_once_with(request, response)

    @mock.patch(
        "openapi_core.validation.response.validators.V31WebhookResponseValidator."
        "validate",
    )
    def test_webhook_request_error(self, mock_validate, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        mock_validate.side_effect = ValueError

        with pytest.raises(ValueError):
            validate_response(request, response, spec=spec_v31)

        mock_validate.assert_called_once_with(request, response)

    def test_webhook_cls(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)
        TestWebhookResp = type(
            "TestWebhookResp",
            (MockRespValidator, WebhookResponseValidator),
            {},
        )

        result = validate_response(
            request, response, spec=spec_v31, cls=TestWebhookResp
        )

        assert result is None
        assert TestWebhookResp.validate_calls == [
            (request, response),
        ]

    def test_webhook_cls_type_invalid(self, spec_v31):
        request = mock.Mock(spec=WebhookRequest)
        response = mock.Mock(spec=Response)

        with pytest.raises(TypeError):
            validate_response(request, response, spec=spec_v31, cls=Exception)
