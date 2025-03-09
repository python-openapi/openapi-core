"""OpenAPI core protocols module"""

from typing import Any
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing_extensions import Annotated
from openapi_core.datatypes import RequestParameters
from typing_extensions import Annotated
from typing_extensions import Doc


@runtime_checkable
class BaseRequest(Protocol):
    parameters: RequestParameters

    @property
    def method(self) -> Annotated[str, Doc("The request method, as lowercase string.")]: ...

    @property
    def body(self) -> Annotated[Optional[bytes], Doc("The request body, as bytes (None if not provided).")]: ...

    @property
    def content_type(self) -> Annotated[str, Doc("The content type with parameters (e.g., charset, boundary, etc.) and always lowercase.")]: ...


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
    def host_url(self) -> Annotated[str, Doc("Url with scheme and host. For example: https://localhost:8000")]: ...

    @property
    def path(self) -> Annotated[str, Doc("Request path.")]: ...


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
    def name(self) -> Annotated[str, Doc("Webhook name.")]: ...


@runtime_checkable
class SupportsPathPattern(Protocol):
    """Supports path_pattern protocol.

    You also need to provide path variables in RequestParameters.

    Attributes:
        path_pattern: The matched path pattern.
            For example: /api/v1/pets/{pet_id}
    """

    @property
    def path_pattern(self) -> Annotated[str, Doc("The matched path pattern. For example: /api/v1/pets/{pet_id}")]: ...


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
    def status_code(self) -> Annotated[int, Doc("The status code as integer.")]: ...

    @property
    def content_type(self) -> Annotated[str, Doc("The content type with parameters and always lowercase.")]: ...

    @property
    def headers(self) -> Annotated[Mapping[str, Any], Doc("Response headers as Headers.")]: ...

    @property
    def data(self) -> Annotated[Optional[bytes], Doc("The response body, as bytes (None if not provided).")]: ...
