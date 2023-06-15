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
    def method(self) -> str:
        ...

    @property
    def body(self) -> Optional[str]:
        ...

    @property
    def mimetype(self) -> str:
        ...


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
        body
            The request body, as string.
        mimetype
            Like content type, but without parameters (eg, without charset,
            type etc.) and always lowercase.
            For example if the content type is "text/HTML; charset=utf-8"
            the mimetype would be "text/html".
    """

    @property
    def host_url(self) -> str:
        ...

    @property
    def path(self) -> str:
        ...


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
        body
            The request body, as string.
        mimetype
            Like content type, but without parameters (eg, without charset,
            type etc.) and always lowercase.
            For example if the content type is "text/HTML; charset=utf-8"
            the mimetype would be "text/html".
    """

    @property
    def name(self) -> str:
        ...


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
    def path_pattern(self) -> str:
        ...


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
