"""OpenAPI core validation response datatypes module"""
import attr

from openapi_core.validation.datatypes import BaseValidationResult


@attr.s
class OpenAPIResponse(object):

    data = attr.ib()
    status_code = attr.ib()

    mimetype = attr.ib()


@attr.s
class ResponseValidationResult(BaseValidationResult):
    data = attr.ib(default=None)
    headers = attr.ib(factory=dict)
