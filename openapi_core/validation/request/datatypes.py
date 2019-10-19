"""OpenAPI core validation request datatypes module"""
import attr
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.datatypes import BaseValidationResult


from six.moves.urllib.parse import urljoin


@attr.s
class RequestParameters(object):
    path = attr.ib(factory=dict)
    query = attr.ib(factory=ImmutableMultiDict)
    header = attr.ib(factory=dict)
    cookie = attr.ib(factory=dict)

    def __getitem__(self, location):
        return getattr(self, location)


@attr.s
class OpenAPIRequest(object):

    host_url = attr.ib()
    path = attr.ib()
    path_pattern = attr.ib()
    method = attr.ib()

    body = attr.ib()

    mimetype = attr.ib()

    parameters = attr.ib(factory=RequestParameters)

    @property
    def full_url_pattern(self):
        return urljoin(self.host_url, self.path_pattern)


@attr.s
class RequestValidationResult(BaseValidationResult):
    body = attr.ib(default=None)
    parameters = attr.ib(factory=RequestParameters)
