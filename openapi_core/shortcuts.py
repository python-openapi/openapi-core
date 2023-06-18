"""OpenAPI core shortcuts module"""
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from openapi_core.exceptions import SpecError
from openapi_core.finders import SpecClasses
from openapi_core.finders import SpecFinder
from openapi_core.finders import SpecVersion
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.spec import Spec
from openapi_core.unmarshalling.request import V30RequestUnmarshaller
from openapi_core.unmarshalling.request import V31RequestUnmarshaller
from openapi_core.unmarshalling.request import V31WebhookRequestUnmarshaller
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.protocols import RequestUnmarshaller
from openapi_core.unmarshalling.request.protocols import (
    WebhookRequestUnmarshaller,
)
from openapi_core.unmarshalling.request.types import AnyRequestUnmarshallerType
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.response import V30ResponseUnmarshaller
from openapi_core.unmarshalling.response import V31ResponseUnmarshaller
from openapi_core.unmarshalling.response import V31WebhookResponseUnmarshaller
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.protocols import ResponseUnmarshaller
from openapi_core.unmarshalling.response.protocols import (
    WebhookResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.types import (
    AnyResponseUnmarshallerType,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.validation.request import V30RequestValidator
from openapi_core.validation.request import V31RequestValidator
from openapi_core.validation.request import V31WebhookRequestValidator
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.protocols import WebhookRequestValidator
from openapi_core.validation.request.types import AnyRequestValidatorType
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
from openapi_core.validation.response import V30ResponseValidator
from openapi_core.validation.response import V31ResponseValidator
from openapi_core.validation.response import V31WebhookResponseValidator
from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.protocols import WebhookResponseValidator
from openapi_core.validation.response.types import AnyResponseValidatorType
from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType

AnyRequest = Union[Request, WebhookRequest]

SPECS: Dict[SpecVersion, SpecClasses] = {
    SpecVersion("openapi", "3.0"): SpecClasses(
        V30RequestValidator,
        V30ResponseValidator,
        None,
        None,
        V30RequestUnmarshaller,
        V30ResponseUnmarshaller,
        None,
        None,
    ),
    SpecVersion("openapi", "3.1"): SpecClasses(
        V31RequestValidator,
        V31ResponseValidator,
        V31WebhookRequestValidator,
        V31WebhookResponseValidator,
        V31RequestUnmarshaller,
        V31ResponseUnmarshaller,
        V31WebhookRequestUnmarshaller,
        V31WebhookResponseUnmarshaller,
    ),
}


def get_classes(spec: Spec) -> SpecClasses:
    return SpecFinder(SPECS).get_classes(spec)


def unmarshal_apicall_request(
    request: Request,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[RequestUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> RequestUnmarshalResult:
    if not isinstance(request, Request):
        raise TypeError("'request' argument is not type of Request")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.request_unmarshaller_cls
    if not issubclass(cls, RequestUnmarshaller):
        raise TypeError("'cls' argument is not type of RequestUnmarshaller")
    v = cls(spec, base_url=base_url, **unmarshaller_kwargs)
    result = v.unmarshal(request)
    result.raise_for_errors()
    return result


def unmarshal_webhook_request(
    request: WebhookRequest,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[WebhookRequestUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> RequestUnmarshalResult:
    if not isinstance(request, WebhookRequest):
        raise TypeError("'request' argument is not type of WebhookRequest")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.webhook_request_unmarshaller_cls
        if cls is None:
            raise SpecError("Unmarshaller class not found")
    if not issubclass(cls, WebhookRequestUnmarshaller):
        raise TypeError(
            "'cls' argument is not type of WebhookRequestUnmarshaller"
        )
    v = cls(spec, base_url=base_url, **unmarshaller_kwargs)
    result = v.unmarshal(request)
    result.raise_for_errors()
    return result


def unmarshal_request(
    request: AnyRequest,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[AnyRequestUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> RequestUnmarshalResult:
    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' argument is not type of (Webhook)Request")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if isinstance(request, WebhookRequest):
        if cls is None or issubclass(cls, WebhookRequestUnmarshaller):
            return unmarshal_webhook_request(
                request,
                spec,
                base_url=base_url,
                cls=cls,
                **unmarshaller_kwargs,
            )
        else:
            raise TypeError(
                "'cls' argument is not type of WebhookRequestUnmarshaller"
            )
    else:
        if cls is None or issubclass(cls, RequestUnmarshaller):
            return unmarshal_apicall_request(
                request,
                spec,
                base_url=base_url,
                cls=cls,
                **unmarshaller_kwargs,
            )
        else:
            raise TypeError(
                "'cls' argument is not type of RequestUnmarshaller"
            )


def unmarshal_apicall_response(
    request: Request,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[ResponseUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> ResponseUnmarshalResult:
    if not isinstance(request, Request):
        raise TypeError("'request' argument is not type of Request")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.response_unmarshaller_cls
    if not issubclass(cls, ResponseUnmarshaller):
        raise TypeError("'cls' argument is not type of ResponseUnmarshaller")
    v = cls(spec, base_url=base_url, **unmarshaller_kwargs)
    result = v.unmarshal(request, response)
    result.raise_for_errors()
    return result


def unmarshal_webhook_response(
    request: WebhookRequest,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[WebhookResponseUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> ResponseUnmarshalResult:
    if not isinstance(request, WebhookRequest):
        raise TypeError("'request' argument is not type of WebhookRequest")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.webhook_response_unmarshaller_cls
        if cls is None:
            raise SpecError("Unmarshaller class not found")
    if not issubclass(cls, WebhookResponseUnmarshaller):
        raise TypeError(
            "'cls' argument is not type of WebhookResponseUnmarshaller"
        )
    v = cls(spec, base_url=base_url, **unmarshaller_kwargs)
    result = v.unmarshal(request, response)
    result.raise_for_errors()
    return result


def unmarshal_response(
    request: AnyRequest,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[AnyResponseUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> ResponseUnmarshalResult:
    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' argument is not type of (Webhook)Request")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if isinstance(request, WebhookRequest):
        if cls is None or issubclass(cls, WebhookResponseUnmarshaller):
            return unmarshal_webhook_response(
                request,
                response,
                spec,
                base_url=base_url,
                cls=cls,
                **unmarshaller_kwargs,
            )
        else:
            raise TypeError(
                "'cls' argument is not type of WebhookResponseUnmarshaller"
            )
    else:
        if cls is None or issubclass(cls, ResponseUnmarshaller):
            return unmarshal_apicall_response(
                request,
                response,
                spec,
                base_url=base_url,
                cls=cls,
                **unmarshaller_kwargs,
            )
        else:
            raise TypeError(
                "'cls' argument is not type of ResponseUnmarshaller"
            )


def validate_request(
    request: AnyRequest,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[AnyRequestValidatorType] = None,
    **validator_kwargs: Any,
) -> Optional[RequestUnmarshalResult]:
    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' argument is not type of (Webhook)Request")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")

    if isinstance(request, WebhookRequest):
        if cls is None or issubclass(cls, WebhookRequestValidator):
            validate_webhook_request(
                request,
                spec,
                base_url=base_url,
                cls=cls,
                **validator_kwargs,
            )
            return None
        else:
            raise TypeError(
                "'cls' argument is not type of WebhookRequestValidator"
            )
    else:
        if cls is None or issubclass(cls, RequestValidator):
            validate_apicall_request(
                request,
                spec,
                base_url=base_url,
                cls=cls,
                **validator_kwargs,
            )
            return None
        else:
            raise TypeError("'cls' argument is not type of RequestValidator")


def validate_response(
    request: Union[Request, WebhookRequest, Spec],
    response: Union[Response, Request, WebhookRequest],
    spec: Union[Spec, Response],
    base_url: Optional[str] = None,
    cls: Optional[AnyResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> Optional[ResponseUnmarshalResult]:
    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' argument is not type of (Webhook)Request")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")

    if isinstance(request, WebhookRequest):
        if cls is None or issubclass(cls, WebhookResponseValidator):
            validate_webhook_response(
                request,
                response,
                spec,
                base_url=base_url,
                cls=cls,
                **validator_kwargs,
            )
            return None
        else:
            raise TypeError(
                "'cls' argument is not type of WebhookResponseValidator"
            )
    else:
        if cls is None or issubclass(cls, ResponseValidator):
            validate_apicall_response(
                request,
                response,
                spec,
                base_url=base_url,
                cls=cls,
                **validator_kwargs,
            )
            return None
        else:
            raise TypeError("'cls' argument is not type of ResponseValidator")


def validate_apicall_request(
    request: Request,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[RequestValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    if not isinstance(request, Request):
        raise TypeError("'request' argument is not type of Request")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.request_validator_cls
    if not issubclass(cls, RequestValidator):
        raise TypeError("'cls' argument is not type of RequestValidator")
    v = cls(spec, base_url=base_url, **validator_kwargs)
    return v.validate(request)


def validate_webhook_request(
    request: WebhookRequest,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[WebhookRequestValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    if not isinstance(request, WebhookRequest):
        raise TypeError("'request' argument is not type of WebhookRequest")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.webhook_request_validator_cls
        if cls is None:
            raise SpecError("Validator class not found")
    if not issubclass(cls, WebhookRequestValidator):
        raise TypeError(
            "'cls' argument is not type of WebhookRequestValidator"
        )
    v = cls(spec, base_url=base_url, **validator_kwargs)
    return v.validate(request)


def validate_apicall_response(
    request: Request,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[ResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    if not isinstance(request, Request):
        raise TypeError("'request' argument is not type of Request")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.response_validator_cls
    if not issubclass(cls, ResponseValidator):
        raise TypeError("'cls' argument is not type of ResponseValidator")
    v = cls(spec, base_url=base_url, **validator_kwargs)
    return v.validate(request, response)


def validate_webhook_response(
    request: WebhookRequest,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    cls: Optional[WebhookResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    if not isinstance(request, WebhookRequest):
        raise TypeError("'request' argument is not type of WebhookRequest")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")
    if cls is None:
        classes = get_classes(spec)
        cls = classes.webhook_response_validator_cls
        if cls is None:
            raise SpecError("Validator class not found")
    if not issubclass(cls, WebhookResponseValidator):
        raise TypeError(
            "'cls' argument is not type of WebhookResponseValidator"
        )
    v = cls(spec, base_url=base_url, **validator_kwargs)
    return v.validate(request, response)
