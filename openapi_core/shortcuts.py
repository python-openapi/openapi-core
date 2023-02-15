"""OpenAPI core validation shortcuts module"""
import warnings
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
from openapi_core.unmarshalling.request.proxies import (
    SpecRequestValidatorProxy,
)
from openapi_core.unmarshalling.request.types import AnyRequestUnmarshallerType
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    BaseAPICallRequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    BaseWebhookRequestUnmarshaller,
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
from openapi_core.unmarshalling.response.proxies import (
    SpecResponseValidatorProxy,
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
from openapi_core.validation.response import V30ResponseValidator
from openapi_core.validation.response import V31ResponseValidator
from openapi_core.validation.response import V31WebhookResponseValidator

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


def unmarshal_request(
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


def unmarshal_response(
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


def validate_request(
    request: AnyRequest,
    spec: Spec,
    base_url: Optional[str] = None,
    validator: Optional[SpecRequestValidatorProxy] = None,
    cls: Optional[AnyRequestUnmarshallerType] = None,
    **validator_kwargs: Any,
) -> RequestUnmarshalResult:
    if isinstance(spec, (Request, WebhookRequest)) and isinstance(
        request, Spec
    ):
        warnings.warn(
            "spec parameter as a first argument is deprecated. "
            "Move it to second argument instead.",
            DeprecationWarning,
        )
        request, spec = spec, request

    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' argument is not type of (Webhook)Request")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")

    if validator is not None and isinstance(request, Request):
        warnings.warn(
            "validator parameter is deprecated. Use cls instead.",
            DeprecationWarning,
        )
        result = validator.validate(spec, request, base_url=base_url)
        result.raise_for_errors()
        return result

    if isinstance(request, WebhookRequest):
        if cls is None or issubclass(cls, WebhookRequestUnmarshaller):
            return unmarshal_webhook_request(
                request, spec, base_url=base_url, cls=cls, **validator_kwargs
            )
        else:
            raise TypeError(
                "'cls' argument is not type of WebhookRequestUnmarshaller"
            )
    elif isinstance(request, Request):
        if cls is None or issubclass(cls, RequestUnmarshaller):
            return unmarshal_request(
                request, spec, base_url=base_url, cls=cls, **validator_kwargs
            )
        else:
            raise TypeError(
                "'cls' argument is not type of RequestUnmarshaller"
            )


def validate_response(
    request: Union[Request, WebhookRequest, Spec],
    response: Union[Response, Request, WebhookRequest],
    spec: Union[Spec, Response],
    base_url: Optional[str] = None,
    validator: Optional[SpecResponseValidatorProxy] = None,
    cls: Optional[AnyResponseUnmarshallerType] = None,
    **validator_kwargs: Any,
) -> ResponseUnmarshalResult:
    if (
        isinstance(request, Spec)
        and isinstance(response, (Request, WebhookRequest))
        and isinstance(spec, Response)
    ):
        warnings.warn(
            "spec parameter as a first argument is deprecated. "
            "Move it to third argument instead.",
            DeprecationWarning,
        )
        args = request, response, spec
        spec, request, response = args

    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' argument is not type of (Webhook)Request")
    if not isinstance(response, Response):
        raise TypeError("'response' argument is not type of Response")
    if not isinstance(spec, Spec):
        raise TypeError("'spec' argument is not type of Spec")

    if validator is not None and isinstance(request, Request):
        warnings.warn(
            "validator parameter is deprecated. Use cls instead.",
            DeprecationWarning,
        )
        result = validator.validate(spec, request, response, base_url=base_url)
        result.raise_for_errors()
        return result

    if isinstance(request, WebhookRequest):
        if cls is None or issubclass(cls, WebhookResponseUnmarshaller):
            return unmarshal_webhook_response(
                request,
                response,
                spec,
                base_url=base_url,
                cls=cls,
                **validator_kwargs,
            )
        else:
            raise TypeError(
                "'cls' argument is not type of WebhookResponseUnmarshaller"
            )
    elif isinstance(request, Request):
        if cls is None or issubclass(cls, ResponseUnmarshaller):
            return unmarshal_response(
                request,
                response,
                spec,
                base_url=base_url,
                cls=cls,
                **validator_kwargs,
            )
        else:
            raise TypeError(
                "'cls' argument is not type of ResponseUnmarshaller"
            )
