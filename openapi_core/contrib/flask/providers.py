"""OpenAPI core contrib flask providers module"""
from typing import Any

from flask.globals import request
from flask.wrappers import Request


class FlaskRequestProvider:
    @classmethod
    def provide(self, *args: Any, **kwargs: Any) -> Request:
        return request
