"""OpenAPI core contrib flask requests module"""
from flask.wrappers import Request
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.werkzeug.requests import WerkzeugOpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class FlaskOpenAPIRequest(WerkzeugOpenAPIRequest):
    def __init__(self, request: Request):
        self.request: Request = request

        self.parameters = RequestParameters(
            path=self.request.view_args or {},
            query=ImmutableMultiDict(self.request.args),
            header=Headers(self.request.headers),
            cookie=self.request.cookies,
        )

    @property
    def path_pattern(self) -> str:
        if self.request.url_rule is None:
            return self.request.path

        return self.path_regex.sub(r"{\1}", self.request.url_rule.rule)
