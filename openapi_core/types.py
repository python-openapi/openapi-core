"""OpenAPI core types"""

from typing import Union

from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest

AnyRequest = Union[Request, WebhookRequest]
