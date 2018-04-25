"""OpenAPI core wrappers module"""
import re
from string import Formatter
import warnings

from urllib.parse import urlparse
from six.moves.urllib.parse import urljoin
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.exceptions import InvalidServer, InvalidOperation


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
            'query': ImmutableMultiDict(args or []),
            'header': headers or {},
            'cookie': cookies or {},
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


class RequestsOpenAPIRequest(BaseOpenAPIRequest):

    def __init__(self, response, path_pattern, regex_pattern, server_pattern):
        """

        :param response: The Requests Responce Object
        :type response: requests.models.Response
        :param path_pattern: The path pattern determined by the factory
        :type path_pattern: str
        :param regex_pattern: Used to extract path params.
        :type regex_pattern: str
        """
        self.response = response
        self.url = urlparse(self.response.url)
        self._path_pattern = path_pattern
        self._regex_pattern = regex_pattern
        self._server_pattern = server_pattern
        self._parameters = {
            'path': self._extract_path_params(),
            'query': self.response.request.qs,
            'headers': self.response.request.headers,
            'cookies': self.response.cookies,
        }

    @property
    def full_url_pattern(self):
        return self.host_url + self.path_pattern

    @property
    def host_url(self):
        return re.match(self._server_pattern, self.response.url).group(0)

    @property
    def path(self):
        return re.sub(self._server_pattern, '', urljoin(self.host_url,
                                                        self.url.path))

    @property
    def method(self):
        return self.response.request.method.lower()

    @property
    def path_pattern(self):
        return self._path_pattern

    @property
    def parameters(self):
        return self._parameters

    def _extract_path_params(self):
        # Get the values of the path parameters
        groups = re.match(self._regex_pattern, self.path).groups()
        # Get the names of path parameters
        names = [fname[1] for fname in Formatter()
                 .parse(self.path_pattern) if fname]
        return {name: group for name, group in zip(names, groups)}

    @property
    def body(self):
        return self.response.request.text

    @property
    def mimetype(self):
        return self.response.request.headers.get('Accept') or\
               self.response.headers.get('Content-Type')


class BaseOpenAPIResponse(object):

    body = NotImplemented
    status_code = NotImplemented

    mimetype = NotImplemented


class MockResponse(BaseOpenAPIRequest):

    def __init__(self, data, status_code=200, mimetype='application/json'):
        self.data = data

        self.status_code = status_code
        self.mimetype = mimetype


class FlaskOpenAPIResponse(BaseOpenAPIResponse):

    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.data

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def mimetype(self):
        return self.response.mimetype


class RequestsOpenAPIResponse(BaseOpenAPIResponse):

    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.text

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def mimetype(self):
        return self.response.headers.get('Content-Type')


class RequestsFactory(object):
    path_regex = re.compile('{(.*?)}')

    def __init__(self, spec):
        """
        Creates the request factory. A spec is required.

        :param spec: The openapi spec to use for decoding the request
        :type spec: openapi_core.specs.Spec
        """
        self.paths_regex = self._create_paths_regex(spec)
        self.server_regex = self._create_server_regex(spec)

    def _create_server_regex(self, spec):
        server_regex = []
        for server in spec.servers:
            var_map = {}
            for var in server.variables:
                if server.variables[var].enum:
                    var_map[var] = "(" +\
                                   "|".join(server.variables[var].enum) + ")"
                else:
                    var_map[var] = "(.*)"
            server_regex.append(server.url.format_map(var_map))
        return server_regex

    def _create_paths_regex(self, spec):
        paths_regex = {}
        for path in spec.paths:
            pattern = self.path_regex.sub('(.*)', path)
            paths_regex[pattern] = path
        return paths_regex

    def _match_operation(self, path_pattern):
        for expr in self.paths_regex:
            if re.fullmatch(expr, path_pattern):
                return expr
        return None

    def _match_server(self, server_pattern):
        for expr in self.server_regex:
            if re.match(expr, server_pattern):
                return expr
        return None

    def create_request(self, response):
        """
        Creates an OpenApi compatible request out of the raw requests request

        :param request: requests.models.Request
        :return: RequestsOpenApiRequest
        """
        server_pattern = self._match_server(response.url)
        if not server_pattern:
            raise InvalidServer("Url server not in spec.")
        path = re.sub(server_pattern, '', response.url)
        pattern = self._match_operation(path)
        if not pattern:
            raise InvalidOperation("Operation not in spec.")
        response = RequestsOpenAPIRequest(
            response, self.paths_regex[pattern], pattern, server_pattern)
        return response

    def create_response(self, response):
        """

        :param request:
        :type request: requests.models.PreparedRequest
        :return: RequestsOpenAPIResponse
        """
        return RequestsOpenAPIResponse(response)
