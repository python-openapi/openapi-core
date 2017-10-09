"""OpenAPI core wrappers module"""
from six import iteritems
from six.moves.urllib.parse import urljoin

from openapi_core.exceptions import (
    OpenAPIMappingError, MissingParameterError, InvalidContentTypeError,
    InvalidServerError,
)

SPEC_LOCATION_TO_REQUEST_LOCATION_MAPPING = {
    'path': 'view_args',
    'query': 'args',
    'headers': 'headers',
    'cookies': 'cookies',
}


class RequestParameters(dict):

    valid_locations = ['path', 'query', 'headers', 'cookies']

    def __getitem__(self, location):
        self.validate_location(location)

        return self.setdefault(location, {})

    def __setitem__(self, location, value):
        raise NotImplementedError

    @classmethod
    def validate_location(cls, location):
        if location not in cls.valid_locations:
            raise OpenAPIMappingError(
                "Unknown parameter location: {0}".format(str(location)))


class BaseRequestFactory(object):

    def get_operation(self, request, spec):
        server = self._get_server(request, spec)

        operation_pattern = request.full_url_pattern.replace(
            server.default_url, '')

        return spec.get_operation(operation_pattern, request.method.lower())

    def _get_server(self, request, spec):
        for server in spec.servers:
            if server.default_url in request.full_url_pattern:
                return server

        raise InvalidServerError(
            "Invalid request server {0}".format(request.full_url_pattern))


class RequestParametersFactory(BaseRequestFactory):

    def __init__(self, attr_mapping=SPEC_LOCATION_TO_REQUEST_LOCATION_MAPPING):
        self.attr_mapping = attr_mapping

    def create(self, request, spec):
        operation = self.get_operation(request, spec)

        params = RequestParameters()
        for param_name, param in iteritems(operation.parameters):
            try:
                value = self._unmarshal_param(request, param)
            except MissingParameterError:
                if param.required:
                    raise
                continue

            params[param.location][param_name] = value
        return params

    def _unmarshal_param(self, request, param):
        request_location = self.attr_mapping[param.location]
        request_attr = getattr(request, request_location)

        try:
            raw_value = request_attr[param.name]
        except KeyError:
            raise MissingParameterError(
                "Missing required `{0}` parameter".format(param.name))

        return param.unmarshal(raw_value)


class RequestBodyFactory(BaseRequestFactory):

    def create(self, request, spec):
        operation = self.get_operation(request, spec)

        if operation.request_body is None:
            return None

        try:
            media_type = operation.request_body[request.mimetype]
        except KeyError:
            raise InvalidContentTypeError(
                "Invalid media type `{0}`".format(request.mimetype))

        return media_type.unmarshal(request.data)


class BaseOpenAPIRequest(object):

    host_url = NotImplemented
    path = NotImplemented
    path_pattern = NotImplemented
    method = NotImplemented

    args = NotImplemented
    view_args = NotImplemented
    headers = NotImplemented
    cookies = NotImplemented

    data = NotImplemented

    mimetype = NotImplemented

    @property
    def full_url_pattern(self):
        return urljoin(self.host_url, self.path_pattern)

    def get_parameters(self, spec):
        return RequestParametersFactory().create(self, spec)

    def get_body(self, spec):
        return RequestBodyFactory().create(self, spec)
