"""OpenAPI core wrappers module"""
import re

from openapi_core.wrappers.base import BaseOpenAPIRequest, BaseOpenAPIResponse

# http://flask.pocoo.org/docs/1.0/quickstart/#variable-rules
PATH_PARAMETER_PATTERN = r'<(?:(?:string|int|float|path|uuid):)?(\w+)>'


class FlaskOpenAPIRequest(BaseOpenAPIRequest):

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    def __init__(self, request):
        self.request = request

    @property
    def host_url(self):
        return self.request.host_url

    @property
    def path(self):
        return self.request.path

    @property
    def method(self):
        return self.request.method.lower()

    @property
    def path_pattern(self):
        if self.request.url_rule is None:
            return self.path

        return self.path_regex.sub(r'{\1}', self.request.url_rule.rule)

    @property
    def parameters(self):
        return {
            'path': self.request.view_args,
            'query': self.request.args,
            'header': self.request.headers,
            'cookie': self.request.cookies,
        }

    @property
    def body(self):
        return self.request.data

    @property
    def mimetype(self):
        return self.request.mimetype


class FlaskOpenAPIResponse(BaseOpenAPIResponse):

    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.data

    @property
    def status_code(self):
        return self.response._status_code

    @property
    def mimetype(self):
        return self.response.mimetype
