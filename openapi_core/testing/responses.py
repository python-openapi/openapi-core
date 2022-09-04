"""OpenAPI core testing responses module"""
from werkzeug.datastructures import Headers


class MockResponse:
    def __init__(
        self, data, status_code=200, headers=None, mimetype="application/json"
    ):
        self.data = data
        self.status_code = status_code
        self.headers = Headers(headers or {})
        self.mimetype = mimetype
