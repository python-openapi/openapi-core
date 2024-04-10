"""OpenAPI core protocols module"""

from typing import Any
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import runtime_checkable

from openapi_core.datatypes import RequestParameters


@runtime_checkable
class BaseRequest(Protocol):
    parameters: RequestParameters

    @property
    def method(self) -> str: ...

    @property
    def body(self) -> Optional[bytes]: ...

    @property
    def content_type(self) -> str: ...


@runtime_checkable
class Request(BaseRequest, Protocol):
    """Request attributes protocol.

    Attributes:
        host_url
            Url with scheme and host
            For example:
            https://localhost:8000
        path
            Request path
        full_url_pattern
            The matched url with scheme, host and path pattern.
            For example:
            https://localhost:8000/api/v1/pets
            https://localhost:8000/api/v1/pets/{pet_id}
        method
            The request method, as lowercase string.
        parameters
            A RequestParameters object. Needs to supports path attribute setter
            to write resolved path parameters.
        content_type
            The content type with parameters (eg, charset, boundary etc.)
            and always lowercase.
        body
            The request body, as bytes (None if not provided).
    """

    @property
    def host_url(self) -> str: ...

    @property
    def path(self) -> str: ...


@runtime_checkable
class WebhookRequest(BaseRequest, Protocol):
    """Webhook request attributes protocol.

    Attributes:
        name
            Webhook name
        method
            The request method, as lowercase string.
        parameters
            A RequestParameters object. Needs to supports path attribute setter
            to write resolved path parameters.
        content_type
            The content type with parameters (eg, charset, boundary etc.)
            and always lowercase.
        body
            The request body, as bytes (None if not provided).
    """

    @property
    def name(self) -> str: ...


@runtime_checkable
class SupportsPathPattern(Protocol):
    """Supports path_pattern attribute protocol.

    You also need to provide path variables in RequestParameters.

    Attributes:
        path_pattern
            The matched path pattern.
            For example:
            /api/v1/pets/{pet_id}
    """

    @property
    def path_pattern(self) -> str: ...


@runtime_checkable
class Response(Protocol):
    """Response protocol.

    Attributes:
        status_code
            The status code as integer.
        headers
            Response headers as Headers.
        content_type
            The content type with parameters and always lowercase.
        data
            The response body, as bytes (None if not provided).
    """

    @property
    def status_code(self) -> int: ...

    @property
    def content_type(self) -> str: ...

    @property
    def headers(self) -> Mapping[str, Any]: ...

    @property
    def data(self) -> Optional[bytes]: ...
