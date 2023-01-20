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

from openapi_core.spec import Spec
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import WebhookRequest
from openapi_core.validation.response.datatypes import ResponseValidationResult


@runtime_checkable
class Response(Protocol):
    """Response protocol.

    Attributes:
        data
            The response body, as string.
        status_code
            The status code as integer.
        headers
            Response headers as Headers.
        mimetype
            Lowercase content type without charset.
    """

    @property
    def data(self) -> str:
        ...

    @property
    def status_code(self) -> int:
        ...

    @property
    def mimetype(self) -> str:
        ...

    @property
    def headers(self) -> Mapping[str, Any]:
        ...


@runtime_checkable
class ResponseValidator(Protocol):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        ...

    def validate(
        self,
        request: Request,
        response: Response,
    ) -> ResponseValidationResult:
        ...


@runtime_checkable
class WebhookResponseValidator(Protocol):
    def __init__(self, spec: Spec, base_url: Optional[str] = None):
        ...

    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseValidationResult:
        ...
