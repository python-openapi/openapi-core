"""OpenAPI core contrib flask providers module"""
from flask import Request
from flask.globals import request


class FlaskRequestProvider:

    @classmethod
    def provide(self, *args, **kwargs) -> Request:
        return request
