"""OpenAPI core validation request datatypes module"""
import attr

from openapi_core.validation.datatypes import BaseValidationResult


@attr.s
class RequestParameters(object):
    path = attr.ib(factory=dict)
    query = attr.ib(factory=dict)
    header = attr.ib(factory=dict)
    cookie = attr.ib(factory=dict)

    def __getitem__(self, location):
        return getattr(self, location)


@attr.s
class RequestValidationResult(BaseValidationResult):
    body = attr.ib(default=None)
    parameters = attr.ib(factory=RequestParameters)
