from dataclasses import dataclass
from typing import Union

from jsonschema._utils import Unset
from jsonschema.validators import _UNSET
from openapi_spec_validator.validation.types import SpecValidatorType

from openapi_core.unmarshalling.configurations import UnmarshallerConfig
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType


@dataclass
class Config(UnmarshallerConfig):
    """OpenAPI configuration dataclass.

    Read more information, in the
    [OpenAPI-core docs for Configuration](https://openapi-core.readthedocs.io/configuration/).

    Attributes:
        spec_validator_cls: Specification validator class.
        spec_base_uri: Specification base URI. Deprecated, use base_uri parameter in OpenAPI.from_dict and OpenAPI.from_file if you want to define it.
        request_validator_cls: Request validator class.
        response_validator_cls: Response validator class.
        webhook_request_validator_cls: Webhook request validator class.
        webhook_response_validator_cls: Webhook response validator class.
        request_unmarshaller_cls: Request unmarshaller class.
        response_unmarshaller_cls: Response unmarshaller class.
        webhook_request_unmarshaller_cls: Webhook request unmarshaller class.
        webhook_response_unmarshaller_cls: Webhook response unmarshaller class.
    """

    spec_validator_cls: Union[SpecValidatorType, Unset] = _UNSET
    spec_base_uri: str = ""

    request_validator_cls: Union[RequestValidatorType, Unset] = _UNSET
    response_validator_cls: Union[ResponseValidatorType, Unset] = _UNSET
    webhook_request_validator_cls: Union[
        WebhookRequestValidatorType, Unset
    ] = _UNSET
    webhook_response_validator_cls: Union[
        WebhookResponseValidatorType, Unset
    ] = _UNSET
    request_unmarshaller_cls: Union[RequestUnmarshallerType, Unset] = _UNSET
    response_unmarshaller_cls: Union[ResponseUnmarshallerType, Unset] = _UNSET
    webhook_request_unmarshaller_cls: Union[
        WebhookRequestUnmarshallerType, Unset
    ] = _UNSET
    webhook_response_unmarshaller_cls: Union[
        WebhookResponseUnmarshallerType, Unset
    ] = _UNSET
