from typing import Type
from typing import Union

from openapi_core.unmarshalling.request.protocols import RequestUnmarshaller
from openapi_core.unmarshalling.request.protocols import (
    WebhookRequestUnmarshaller,
)

RequestUnmarshallerType = Type[RequestUnmarshaller]
WebhookRequestUnmarshallerType = Type[WebhookRequestUnmarshaller]
AnyRequestUnmarshallerType = Union[
    RequestUnmarshallerType, WebhookRequestUnmarshallerType
]
