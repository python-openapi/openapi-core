"""OpenAPI core wrappers module"""
from six import iteritems

from openapi_core.exceptions import (
    OpenAPIMappingError, MissingParameterError, InvalidContentTypeError,
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


class RequestParametersFactory(object):

    def __init__(self, attr_mapping=SPEC_LOCATION_TO_REQUEST_LOCATION_MAPPING):
        self.attr_mapping = attr_mapping

    def create(self, request, spec):
        operation = spec.get_operation(request.path_pattern, request.method)

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


class RequestBodyFactory(object):

    def create(self, request, spec):
        operation = spec.get_operation(request.path_pattern, request.method)

        try:
            media_type = operation.request_body[request.content_type]
        except KeyError:
            raise InvalidContentTypeError(
                "Invalid Content-Type `{0}`".format(request.content_type))

        return media_type.unmarshal(request.data)


class BaseOpenAPIRequest(object):

    path = NotImplemented
    path_pattern = NotImplemented
    method = NotImplemented

    args = NotImplemented
    view_args = NotImplemented
    headers = NotImplemented
    cookies = NotImplemented

    data = NotImplemented

    content_type = NotImplemented

    def get_parameters(self, spec):
        return RequestParametersFactory().create(self, spec)

    def get_body(self, spec):
        return RequestBodyFactory().create(self, spec)
