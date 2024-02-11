"""OpenAPI core contrib flask requests module"""

from flask.wrappers import Request
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.werkzeug.requests import WerkzeugOpenAPIRequest
from openapi_core.datatypes import RequestParameters


class FlaskOpenAPIRequest(WerkzeugOpenAPIRequest):
    def __init__(self, request: Request):
        if not isinstance(request, Request):
            raise TypeError(f"'request' argument is not type of {Request}")
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
            return self.path

        path = self.get_path(self.request.url_rule.rule)
        return self.path_regex.sub(r"{\1}", path)
