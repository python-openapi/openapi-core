"""OpenAPI core validation request protocols module"""
import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Protocol
    from typing import runtime_checkable
else:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable

from openapi_core.spec import Spec
from openapi_core.validation.request.datatypes import RequestParameters
from openapi_core.validation.request.datatypes import RequestValidationResult


@runtime_checkable
class Request(Protocol):
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

    parameters: RequestParameters

    @property
    def host_url(self) -> str:
        ...

    @property
    def path(self) -> str:
        ...

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
class RequestValidator(Protocol):
    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        ...
