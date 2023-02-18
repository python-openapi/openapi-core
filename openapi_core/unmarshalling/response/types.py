from typing import Type
from typing import Union

from openapi_core.unmarshalling.response.protocols import ResponseUnmarshaller
from openapi_core.unmarshalling.response.protocols import (
    WebhookResponseUnmarshaller,
)

ResponseUnmarshallerType = Type[ResponseUnmarshaller]
WebhookResponseUnmarshallerType = Type[WebhookResponseUnmarshaller]
AnyResponseUnmarshallerType = Union[
    ResponseUnmarshallerType, WebhookResponseUnmarshallerType
]
