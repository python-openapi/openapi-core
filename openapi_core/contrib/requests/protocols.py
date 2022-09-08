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

from requests.cookies import RequestsCookieJar


@runtime_checkable
class SupportsCookieJar(Protocol):
    _cookies: RequestsCookieJar
