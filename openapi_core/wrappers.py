"""OpenAPI core wrappers module"""
import warnings

from six.moves.urllib.parse import urljoin


class BaseOpenAPIRequest(object):

    host_url = NotImplemented
    path = NotImplemented
    path_pattern = NotImplemented
    method = NotImplemented

    parameters = NotImplemented
    body = NotImplemented

    mimetype = NotImplemented

    @property
    def full_url_pattern(self):
        return urljoin(self.host_url, self.path_pattern)

    def get_body(self, spec):
        warnings.warn(
            "`get_body` method is deprecated. "
            "Use RequestValidator instead.",
            DeprecationWarning,
        )
        # backward compatibility
        from openapi_core.shortcuts import validate_body
        return validate_body(spec, self, wrapper_class=None)

    def get_parameters(self, spec):
        warnings.warn(
            "`get_parameters` method is deprecated. "
            "Use RequestValidator instead.",
            DeprecationWarning,
        )
        # backward compatibility
        from openapi_core.shortcuts import validate_parameters
        return validate_parameters(spec, self, wrapper_class=None)


class MockRequest(BaseOpenAPIRequest):

    def __init__(
            self, host_url, method, path, path_pattern=None, args=None,
            view_args=None, headers=None, cookies=None, data=None,
            mimetype='application/json'):
        self.host_url = host_url
        self.path = path
        self.path_pattern = path_pattern or path
        self.method = method.lower()

        self.parameters = {
            'path': view_args or {},
            'query': args or {},
            'headers': headers or {},
            'cookies': cookies or {},
        }

        self.body = data or ''

        self.mimetype = mimetype


class FlaskOpenAPIRequest(BaseOpenAPIRequest):

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

        return self.request.url_rule.rule

    @property
    def parameters(self):
        return {
            'path': self.request.view_args,
            'query': self.request.args,
            'headers': self.request.headers,
            'cookies': self.request.cookies,
        }

    @property
    def body(self):
        return self.request.data

    @property
    def mimetype(self):
        return self.request.mimetype
