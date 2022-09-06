"""OpenAPI core validation processors module"""


class OpenAPIProcessor:
    def __init__(self, request_validator, response_validator):
        self.request_validator = request_validator
        self.response_validator = response_validator

    def process_request(self, spec, request):
        return self.request_validator.validate(spec, request)

    def process_response(self, spec, request, response):
        return self.response_validator.validate(spec, request, response)
