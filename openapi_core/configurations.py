import warnings
from dataclasses import dataclass
from dataclasses import field
from functools import lru_cache
from pathlib import Path
from typing import Any
from typing import Hashable
from typing import Mapping
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from jsonschema._utils import Unset
from jsonschema.validators import _UNSET
from jsonschema_path import SchemaPath
from jsonschema_path.handlers.protocols import SupportsRead
from jsonschema_path.typing import Schema
from openapi_spec_validator import validate
from openapi_spec_validator.validation.types import SpecValidatorType
from openapi_spec_validator.versions.datatypes import SpecVersion
from openapi_spec_validator.versions.exceptions import OpenAPIVersionNotFound
from openapi_spec_validator.versions.shortcuts import get_spec_version

from openapi_core.exceptions import SpecError
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.types import AnyRequest
from openapi_core.unmarshalling.configurations import UnmarshallerConfig
from openapi_core.unmarshalling.request import (
    UNMARSHALLERS as REQUEST_UNMARSHALLERS,
)
from openapi_core.unmarshalling.request import (
    WEBHOOK_UNMARSHALLERS as WEBHOOK_REQUEST_UNMARSHALLERS,
)
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.protocols import RequestUnmarshaller
from openapi_core.unmarshalling.request.protocols import (
    WebhookRequestUnmarshaller,
)
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.response import (
    UNMARSHALLERS as RESPONSE_UNMARSHALLERS,
)
from openapi_core.unmarshalling.response import (
    WEBHOOK_UNMARSHALLERS as WEBHOOK_RESPONSE_UNMARSHALLERS,
)
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.protocols import ResponseUnmarshaller
from openapi_core.unmarshalling.response.protocols import (
    WebhookResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.validation.request import VALIDATORS as REQUEST_VALIDATORS
from openapi_core.validation.request import (
    WEBHOOK_VALIDATORS as WEBHOOK_REQUEST_VALIDATORS,
)
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.protocols import WebhookRequestValidator
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
from openapi_core.validation.response import VALIDATORS as RESPONSE_VALIDATORS
from openapi_core.validation.response import (
    WEBHOOK_VALIDATORS as WEBHOOK_RESPONSE_VALIDATORS,
)
from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.protocols import WebhookResponseValidator
from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType


@dataclass
class Config(UnmarshallerConfig):
    """OpenAPI configuration dataclass.

    Attributes:
        spec_validator_cls
            Specifincation validator class.
        spec_base_uri
            Specification base uri.
        request_validator_cls
            Request validator class.
        response_validator_cls
            Response validator class.
        webhook_request_validator_cls
            Webhook request validator class.
        webhook_response_validator_cls
            Webhook response validator class.
        request_unmarshaller_cls
            Request unmarshaller class.
        response_unmarshaller_cls
            Response unmarshaller class.
        webhook_request_unmarshaller_cls
            Webhook request unmarshaller class.
        webhook_response_unmarshaller_cls
            Webhook response unmarshaller class.
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
