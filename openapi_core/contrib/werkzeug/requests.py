"""OpenAPI core contrib werkzeug requests module"""
import re
from typing import Optional

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.wrappers import Request

from openapi_core.validation.request.datatypes import RequestParameters

# http://flask.pocoo.org/docs/1.0/quickstart/#variable-rules
PATH_PARAMETER_PATTERN = r"<(?:(?:string|int|float|path|uuid):)?(\w+)>"


class WerkzeugOpenAPIRequest:

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    def __init__(self, request: Request):
        self.request = request

        self.parameters = RequestParameters(
            query=ImmutableMultiDict(self.request.args),
            header=Headers(self.request.headers),
            cookie=self.request.cookies,
        )

    @property
    def host_url(self) -> str:
        return self.request.host_url

    @property
    def path(self) -> str:
        return self.get_path(self.request.path)

    @property
    def method(self) -> str:
        return self.request.method.lower()

    @property
    def body(self) -> Optional[str]:
        return self.request.get_data(as_text=True)

    @property
    def mimetype(self) -> str:
        return self.request.mimetype

    def get_path(self, path: str) -> str:
        return "".join([self.request.root_path, path])
