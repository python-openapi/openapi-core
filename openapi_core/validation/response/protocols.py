"""OpenAPI core validation response protocols module"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable
else:
    try:
        from typing import Protocol
        from typing import runtime_checkable
    except ImportError:
        from typing_extensions import Protocol
        from typing_extensions import runtime_checkable

from werkzeug.datastructures import Headers


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
    def headers(self) -> Headers:
        ...
