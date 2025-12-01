"""OpenAPI core protocols"""

from typing import Any
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import Union
from typing import runtime_checkable

from werkzeug.datastructures import Headers

from openapi_core.datatypes import RequestParameters

# Type alias for headers that accepts both Mapping and werkzeug Headers
HeadersType = Union[Mapping[str, Any], Headers]


@runtime_checkable
class BaseRequest(Protocol):
    parameters: RequestParameters

    @property
    def method(self) -> str:
        """The request method, as lowercase string."""

    @property
    def body(self) -> Optional[bytes]:
        """The request body, as bytes (None if not provided)."""

    @property
    def content_type(self) -> str:
        """The content type with parameters (e.g., charset, boundary, etc.) and always lowercase."""


@runtime_checkable
class Request(BaseRequest, Protocol):
    """Request protocol.

    Attributes:
        host_url: Url with scheme and host.
            For example: https://localhost:8000
        path: Request path.
        full_url_pattern: The matched url with scheme, host and path pattern.
            For example: https://localhost:8000/api/v1/pets
                         https://localhost:8000/api/v1/pets/{pet_id}
        method: The request method, as lowercase string.
        parameters: A RequestParameters object. Needs to support path attribute setter
            to write resolved path parameters.
        content_type: The content type with parameters (e.g., charset, boundary, etc.)
            and always lowercase.
        body: The request body, as bytes (None if not provided).
    """

    @property
    def host_url(self) -> str:
        """Url with scheme and host. For example: https://localhost:8000"""

    @property
    def path(self) -> str:
        """Request path."""


@runtime_checkable
class WebhookRequest(BaseRequest, Protocol):
    """Webhook request protocol.

    Attributes:
        name: Webhook name.
        method: The request method, as lowercase string.
        parameters: A RequestParameters object. Needs to support path attribute setter
            to write resolved path parameters.
        content_type: The content type with parameters (e.g., charset, boundary, etc.)
            and always lowercase.
        body: The request body, as bytes (None if not provided).
    """

    @property
    def name(self) -> str:
        """Webhook name."""


@runtime_checkable
class SupportsPathPattern(Protocol):
    """Supports path_pattern protocol.

    You also need to provide path variables in RequestParameters.

    Attributes:
        path_pattern: The matched path pattern.
            For example: /api/v1/pets/{pet_id}
    """

    @property
    def path_pattern(self) -> str:
        """The matched path pattern. For example: /api/v1/pets/{pet_id}"""


@runtime_checkable
class Response(Protocol):
    """Response protocol.

    Attributes:
        status_code: The status code as integer.
        headers: Response headers as Headers.
        content_type: The content type with parameters and always lowercase.
        data: The response body, as bytes (None if not provided).
    """

    @property
    def status_code(self) -> int:
        """The status code as integer."""

    @property
    def content_type(self) -> str:
        """The content type with parameters and always lowercase."""

    @property
    def headers(self) -> HeadersType:
        """Response headers as Headers."""

    @property
    def data(self) -> Optional[bytes]:
        """The response body, as bytes (None if not provided)."""
