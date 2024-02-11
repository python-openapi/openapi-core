"""OpenAPI core shortcuts module"""

from typing import Any
from typing import Optional
from typing import Union

from jsonschema.validators import _UNSET
from jsonschema_path import SchemaPath

from openapi_core.app import OpenAPI
from openapi_core.configurations import Config
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.types import AnyRequest
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.types import AnyRequestUnmarshallerType
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.types import (
    AnyResponseUnmarshallerType,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.validation.request.types import AnyRequestValidatorType
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
from openapi_core.validation.response.types import AnyResponseValidatorType
from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType


def unmarshal_apicall_request(
    request: Request,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[RequestUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> RequestUnmarshalResult:
    config = Config(
        server_base_url=base_url,
        request_unmarshaller_cls=cls or _UNSET,
        **unmarshaller_kwargs,
    )
    result = OpenAPI(spec, config=config).unmarshal_apicall_request(request)
    result.raise_for_errors()
    return result


def unmarshal_webhook_request(
    request: WebhookRequest,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[WebhookRequestUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> RequestUnmarshalResult:
    config = Config(
        server_base_url=base_url,
        webhook_request_unmarshaller_cls=cls or _UNSET,
        **unmarshaller_kwargs,
    )
    result = OpenAPI(spec, config=config).unmarshal_webhook_request(request)
    result.raise_for_errors()
    return result


def unmarshal_request(
    request: AnyRequest,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[AnyRequestUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> RequestUnmarshalResult:
    config = Config(
        server_base_url=base_url,
        request_unmarshaller_cls=cls or _UNSET,
        webhook_request_unmarshaller_cls=cls or _UNSET,
        **unmarshaller_kwargs,
    )
    result = OpenAPI(spec, config=config).unmarshal_request(request)
    result.raise_for_errors()
    return result


def unmarshal_apicall_response(
    request: Request,
    response: Response,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[ResponseUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> ResponseUnmarshalResult:
    config = Config(
        server_base_url=base_url,
        response_unmarshaller_cls=cls or _UNSET,
        **unmarshaller_kwargs,
    )
    result = OpenAPI(spec, config=config).unmarshal_apicall_response(
        request, response
    )
    result.raise_for_errors()
    return result


def unmarshal_webhook_response(
    request: WebhookRequest,
    response: Response,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[WebhookResponseUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> ResponseUnmarshalResult:
    config = Config(
        server_base_url=base_url,
        webhook_response_unmarshaller_cls=cls or _UNSET,
        **unmarshaller_kwargs,
    )
    result = OpenAPI(spec, config=config).unmarshal_webhook_response(
        request, response
    )
    result.raise_for_errors()
    return result


def unmarshal_response(
    request: AnyRequest,
    response: Response,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[AnyResponseUnmarshallerType] = None,
    **unmarshaller_kwargs: Any,
) -> ResponseUnmarshalResult:
    config = Config(
        server_base_url=base_url,
        response_unmarshaller_cls=cls or _UNSET,
        webhook_response_unmarshaller_cls=cls or _UNSET,
        **unmarshaller_kwargs,
    )
    result = OpenAPI(spec, config=config).unmarshal_response(request, response)
    result.raise_for_errors()
    return result


def validate_request(
    request: AnyRequest,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[AnyRequestValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    config = Config(
        server_base_url=base_url,
        request_validator_cls=cls or _UNSET,
        webhook_request_validator_cls=cls or _UNSET,
        **validator_kwargs,
    )
    return OpenAPI(spec, config=config).validate_request(request)


def validate_response(
    request: Union[Request, WebhookRequest],
    response: Response,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[AnyResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    config = Config(
        server_base_url=base_url,
        response_validator_cls=cls or _UNSET,
        webhook_response_validator_cls=cls or _UNSET,
        **validator_kwargs,
    )
    return OpenAPI(spec, config=config).validate_response(request, response)


def validate_apicall_request(
    request: Request,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[RequestValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    config = Config(
        server_base_url=base_url,
        request_validator_cls=cls or _UNSET,
        **validator_kwargs,
    )
    return OpenAPI(spec, config=config).validate_apicall_request(request)


def validate_webhook_request(
    request: WebhookRequest,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[WebhookRequestValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    config = Config(
        server_base_url=base_url,
        webhook_request_validator_cls=cls or _UNSET,
        **validator_kwargs,
    )
    return OpenAPI(spec, config=config).validate_webhook_request(request)


def validate_apicall_response(
    request: Request,
    response: Response,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[ResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    config = Config(
        server_base_url=base_url,
        response_validator_cls=cls or _UNSET,
        **validator_kwargs,
    )
    return OpenAPI(spec, config=config).validate_apicall_response(
        request, response
    )


def validate_webhook_response(
    request: WebhookRequest,
    response: Response,
    spec: SchemaPath,
    base_url: Optional[str] = None,
    cls: Optional[WebhookResponseValidatorType] = None,
    **validator_kwargs: Any,
) -> None:
    config = Config(
        server_base_url=base_url,
        webhook_response_validator_cls=cls or _UNSET,
        **validator_kwargs,
    )
    return OpenAPI(spec, config=config).validate_webhook_response(
        request, response
    )
