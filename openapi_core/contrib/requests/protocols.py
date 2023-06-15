from typing import Protocol
from typing import runtime_checkable

from requests.cookies import RequestsCookieJar


@runtime_checkable
class SupportsCookieJar(Protocol):
    _cookies: RequestsCookieJar
