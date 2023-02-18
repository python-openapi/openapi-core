"""OpenAPI core validation response protocols module"""
import sys
from typing import Iterator
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


@runtime_checkable
class ResponseValidator(Protocol):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        ...

    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        ...

    def validate(
        self,
        request: Request,
        response: Response,
    ) -> None:
        ...


@runtime_checkable
class WebhookResponseValidator(Protocol):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        ...

    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        ...

    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> None:
        ...
