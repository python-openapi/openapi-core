"""OpenAPI core validation response models module"""
from openapi_core.validation.models import BaseValidationResult


class ResponseValidationResult(BaseValidationResult):

    def __init__(self, errors, data=None, headers=None):
        super(ResponseValidationResult, self).__init__(errors)
        self.data = data
        self.headers = headers
