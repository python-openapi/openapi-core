import sys

if sys.version_info >= (3, 8):
    from typing import Protocol
    from typing import runtime_checkable
else:
    from typing_extensions import Protocol
    from typing_extensions import runtime_checkable

from requests.cookies import RequestsCookieJar


@runtime_checkable
class SupportsCookieJar(Protocol):
    _cookies: RequestsCookieJar
