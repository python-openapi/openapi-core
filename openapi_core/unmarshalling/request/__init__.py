"""OpenAPI core unmarshalling request module"""

from typing import Mapping

from openapi_spec_validator.versions import consts as versions
from openapi_spec_validator.versions.datatypes import SpecVersion

from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V31RequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V31WebhookRequestUnmarshaller,
)

__all__ = [
    "UNMARSHALLERS",
    "WEBHOOK_UNMARSHALLERS",
    "V3RequestUnmarshaller",
    "V3WebhookRequestUnmarshaller",
    "V30RequestUnmarshaller",
    "V31RequestUnmarshaller",
    "V31WebhookRequestUnmarshaller",
]

# versions mapping
UNMARSHALLERS: Mapping[SpecVersion, RequestUnmarshallerType] = {
    versions.OPENAPIV30: V30RequestUnmarshaller,
    versions.OPENAPIV31: V31RequestUnmarshaller,
}
WEBHOOK_UNMARSHALLERS: Mapping[SpecVersion, WebhookRequestUnmarshallerType] = {
    versions.OPENAPIV31: V31WebhookRequestUnmarshaller,
}

# alias to the latest v3 version
V3RequestUnmarshaller = V31RequestUnmarshaller
V3WebhookRequestUnmarshaller = V31WebhookRequestUnmarshaller
