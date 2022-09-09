"""OpenAPI core contrib django requests module"""
import re
from typing import Optional

from django.http.request import HttpRequest
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.request.datatypes import RequestParameters

# https://docs.djangoproject.com/en/2.2/topics/http/urls/
#
# Currently unsupported are :
#   - nested arguments, e.g.: ^comments/(?:page-(?P<page_number>\d+)/)?$
#   - unnamed regex groups, e.g.: ^articles/([0-9]{4})/$
#   - multiple named parameters between a single pair of slashes
#     e.g.: <page_slug>-<page_id>/edit/
#
# The regex matches everything, except a "/" until "<". Than only the name
# is exported, after which it matches ">" and everything until a "/".
PATH_PARAMETER_PATTERN = r"(?:[^\/]*?)<(?:(?:.*?:))*?(\w+)>(?:[^\/]*)"


class DjangoOpenAPIRequest:

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    def __init__(self, request: HttpRequest):
        self.request = request

        path = (
            self.request.resolver_match
            and self.request.resolver_match.kwargs
            or {}
        )
        self.parameters = RequestParameters(
            path=path,
            query=ImmutableMultiDict(self.request.GET),
            header=Headers(self.request.headers.items()),
            cookie=ImmutableMultiDict(dict(self.request.COOKIES)),
        )

    @property
    def host_url(self) -> str:
        assert isinstance(self.request._current_scheme_host, str)
        return self.request._current_scheme_host

    @property
    def path(self) -> str:
        assert isinstance(self.request.path, str)
        return self.request.path

    @property
    def path_pattern(self) -> Optional[str]:
        if self.request.resolver_match is None:
            return None

        route = self.path_regex.sub(r"{\1}", self.request.resolver_match.route)
        # Delete start and end marker to allow concatenation.
        if route[:1] == "^":
            route = route[1:]
        if route[-1:] == "$":
            route = route[:-1]
        return "/" + route

    @property
    def method(self) -> str:
        if self.request.method is None:
            return ""
        assert isinstance(self.request.method, str)
        return self.request.method.lower()

    @property
    def body(self) -> str:
        assert isinstance(self.request.body, bytes)
        return self.request.body.decode("utf-8")

    @property
    def mimetype(self) -> str:
        return self.request.content_type or ""
