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
from openapi_core.unmarshalling.response.unmarshallers import (
    V32ResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V32WebhookResponseUnmarshaller,
)

__all__ = [
    "UNMARSHALLERS",
    "WEBHOOK_UNMARSHALLERS",
    "V3ResponseUnmarshaller",
    "V3WebhookResponseUnmarshaller",
    "V30ResponseUnmarshaller",
    "V31ResponseUnmarshaller",
    "V31WebhookResponseUnmarshaller",
    "V32ResponseUnmarshaller",
    "V32WebhookResponseUnmarshaller",
]

# versions mapping
UNMARSHALLERS: Mapping[SpecVersion, ResponseUnmarshallerType] = {
    versions.OPENAPIV30: V30ResponseUnmarshaller,
    versions.OPENAPIV31: V31ResponseUnmarshaller,
    versions.OPENAPIV32: V32ResponseUnmarshaller,
}
WEBHOOK_UNMARSHALLERS: Mapping[
    SpecVersion, WebhookResponseUnmarshallerType
] = {
    versions.OPENAPIV31: V31WebhookResponseUnmarshaller,
    versions.OPENAPIV32: V32WebhookResponseUnmarshaller,
}

# alias to the latest v3 version
V3ResponseUnmarshaller = V32ResponseUnmarshaller
V3WebhookResponseUnmarshaller = V32WebhookResponseUnmarshaller
