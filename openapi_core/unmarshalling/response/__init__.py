"""OpenAPI core unmarshalling response module"""

from typing import Mapping

from openapi_spec_validator.versions import consts as versions
from openapi_spec_validator.versions.datatypes import SpecVersion

from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V31ResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V31WebhookResponseUnmarshaller,
)

__all__ = [
    "UNMARSHALLERS",
    "WEBHOOK_UNMARSHALLERS",
    "V3ResponseUnmarshaller",
    "V3WebhookResponseUnmarshaller",
    "V30ResponseUnmarshaller",
    "V31ResponseUnmarshaller",
    "V31WebhookResponseUnmarshaller",
]

# versions mapping
UNMARSHALLERS: Mapping[SpecVersion, ResponseUnmarshallerType] = {
    versions.OPENAPIV30: V30ResponseUnmarshaller,
    versions.OPENAPIV31: V31ResponseUnmarshaller,
}
WEBHOOK_UNMARSHALLERS: Mapping[
    SpecVersion, WebhookResponseUnmarshallerType
] = {
    versions.OPENAPIV31: V31WebhookResponseUnmarshaller,
}

# alias to the latest v3 version
V3ResponseUnmarshaller = V31ResponseUnmarshaller
V3WebhookResponseUnmarshaller = V31WebhookResponseUnmarshaller
