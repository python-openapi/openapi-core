"""OpenAPI core validation processors module"""
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPIProcessor(object):

    def __init__(self, request_validator, response_validator):
        self.request_validator = request_validator
        self.response_validator = response_validator

    def process_request(self, request):
        request_result = self.request_validator.validate(request)
        try:
            request_result.raise_for_errors()
        # return instantly on server error
        except InvalidServer as exc:
            return [exc, ]
        except OpenAPIMappingError:
            return request_result.errors
        else:
            return

    def process_response(self, request, response):
        response_result = self.response_validator.validate(request, response)
        try:
            response_result.raise_for_errors()
        except OpenAPIMappingError:
            return response_result.errors
        else:
            return
