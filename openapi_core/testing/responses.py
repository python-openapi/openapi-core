"""OpenAPI core testing responses module"""
from typing import Any
from typing import Dict
from typing import Optional

from werkzeug.datastructures import Headers


class MockResponse:
    def __init__(
        self,
        data: str,
        status_code: int = 200,
        headers: Optional[Dict[str, Any]] = None,
        mimetype: str = "application/json",
    ):
        self.data = data
        self.status_code = status_code
        self.headers = Headers(headers or {})
        self.mimetype = mimetype
