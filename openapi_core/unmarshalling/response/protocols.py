"""OpenAPI core validation response protocols module"""
import sys
from typing import Any
from typing import Mapping
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Protocol
    from typing import runtime_checkable
else:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.spec import Spec
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)


@runtime_checkable
class ResponseUnmarshaller(Protocol):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        ...

    def unmarshal(
        self,
        request: Request,
        response: Response,
    ) -> ResponseUnmarshalResult:
        ...


@runtime_checkable
class WebhookResponseUnmarshaller(Protocol):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        ...

    def unmarshal(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseUnmarshalResult:
        ...
