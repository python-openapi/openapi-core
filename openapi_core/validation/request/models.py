"""OpenAPI core validation request models module"""
from openapi_core.schema.exceptions import OpenAPIMappingError

from openapi_core.validation.models import BaseValidationResult


class RequestParameters(dict):

    valid_locations = ['path', 'query', 'header', 'cookie']

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


class RequestValidationResult(BaseValidationResult):

    def __init__(self, errors, body=None, parameters=None):
        super(RequestValidationResult, self).__init__(errors)
        self.body = body
        self.parameters = parameters or RequestParameters()
