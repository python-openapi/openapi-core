"""OpenAPI core validation shortcuts module"""
import warnings
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import Type
from typing import Union

from openapi_core.spec import Spec
from openapi_core.validation.exceptions import ValidatorDetectError
from openapi_core.validation.request import V30RequestValidator
from openapi_core.validation.request import V31RequestValidator
from openapi_core.validation.request import V31WebhookRequestValidator
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.protocols import WebhookRequest
from openapi_core.validation.request.protocols import WebhookRequestValidator
from openapi_core.validation.request.proxies import SpecRequestValidatorProxy
from openapi_core.validation.response import V30ResponseValidator
from openapi_core.validation.response import V31ResponseValidator
from openapi_core.validation.response import V31WebhookResponseValidator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.protocols import WebhookResponseValidator
from openapi_core.validation.response.proxies import SpecResponseValidatorProxy

AnyRequest = Union[Request, WebhookRequest]
RequestValidatorType = Type[RequestValidator]
ResponseValidatorType = Type[ResponseValidator]
WebhookRequestValidatorType = Type[WebhookRequestValidator]
WebhookResponseValidatorType = Type[WebhookResponseValidator]
AnyRequestValidatorType = Union[
    RequestValidatorType, WebhookRequestValidatorType
]
AnyResponseValidatorType = Union[
    ResponseValidatorType, WebhookResponseValidatorType
]


class SpecVersion(NamedTuple):
    name: str
    version: str


class SpecValidators(NamedTuple):
    request_cls: Type[RequestValidator]
    response_cls: Type[ResponseValidator]
    webhook_request_cls: Optional[Type[WebhookRequestValidator]]
    webhook_response_cls: Optional[Type[WebhookResponseValidator]]


SPECS: Dict[SpecVersion, SpecValidators] = {
    SpecVersion("openapi", "3.0"): SpecValidators(
        V30RequestValidator,
        V30ResponseValidator,
        None,
        None,
    ),
    SpecVersion("openapi", "3.1"): SpecValidators(
        V31RequestValidator,
        V31ResponseValidator,
        V31WebhookRequestValidator,
        V31WebhookResponseValidator,
    ),
}


def get_validators(spec: Spec) -> SpecValidators:
    for v, validators in SPECS.items():
        if v.name in spec and spec[v.name].startswith(v.version):
            return validators
    raise ValidatorDetectError("Spec schema version not detected")


def validate_request(
    request: AnyRequest,
    spec: Spec,
    base_url: Optional[str] = None,
    validator: Optional[SpecRequestValidatorProxy] = None,
    cls: Optional[AnyRequestValidatorType] = None,
    **validator_kwargs: Any,
) -> RequestValidationResult:
    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' is not (Webhook)Request")
    if validator is not None and isinstance(request, Request):
        warnings.warn(
            "validator parameter is deprecated. Use cls instead.",
            DeprecationWarning,
        )
        result = validator.validate(spec, request, base_url=base_url)
    else:
        if cls is None:
            validators = get_validators(spec)
            if isinstance(request, WebhookRequest):
                cls = validators.webhook_request_cls
            else:
                cls = validators.request_cls
            if cls is None:
                raise ValidatorDetectError("Validator not found")
        assert (
            isinstance(cls, RequestValidator) and isinstance(request, Request)
        ) or (
            isinstance(cls, WebhookRequestValidator)
            and isinstance(request, WebhookRequest)
        )
        v = cls(spec, base_url=base_url, **validator_kwargs)
        result = v.validate(request)
    result.raise_for_errors()
    return result


def validate_response(
    request: AnyRequest,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    validator: Optional[SpecResponseValidatorProxy] = None,
    cls: Optional[AnyResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> ResponseValidationResult:
    if not isinstance(request, (Request, WebhookRequest)):
        raise TypeError("'request' is not (Webhook)Request")
    if not isinstance(response, Response):
        raise TypeError("'response' is not Response")
    if validator is not None and isinstance(request, Request):
        warnings.warn(
            "validator parameter is deprecated. Use cls instead.",
            DeprecationWarning,
        )
        result = validator.validate(spec, request, response, base_url=base_url)
    else:
        if cls is None:
            validators = get_validators(spec)
            if isinstance(request, WebhookRequest):
                cls = validators.webhook_response_cls
            else:
                cls = validators.response_cls
            if cls is None:
                raise ValidatorDetectError("Validator not found")
        assert (
            isinstance(cls, ResponseValidator) and isinstance(request, Request)
        ) or (
            isinstance(cls, WebhookResponseValidator)
            and isinstance(request, WebhookRequest)
        )
        v = cls(spec, base_url=base_url, **validator_kwargs)
        result = v.validate(request, response)
    result.raise_for_errors()
    return result
