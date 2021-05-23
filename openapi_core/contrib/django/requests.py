"""OpenAPI core contrib django requests module"""
import re
from typing import Dict
from urllib.parse import urljoin

from django.http.request import HttpRequest
from werkzeug.datastructures import ImmutableMultiDict, Headers

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)
from openapi_core.validation.request.factories import BaseOpenAPIRequestFactory

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
PATH_PARAMETER_PATTERN = r'(?:[^\/]*?)<(?:(?:.*?:))*?(\w+)>(?:[^\/]*)'


class DjangoOpenAPIRequestFactory(BaseOpenAPIRequestFactory):

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    def create(self, request: HttpRequest) -> OpenAPIRequest:
        assert request.content_type is not None
        assert request.method is not None

        return OpenAPIRequest(
            full_url_pattern=self._get_full_url_pattern(request),
            method=self._get_method(request),
            parameters=self._get_parameters(request),
            body=self._get_body(request),
            mimetype=self._get_mimetype(request),
        )

    def _get_parameters(self, request: HttpRequest) -> RequestParameters:
        return RequestParameters(
            path=self._get_path(request),
            query=self._get_query(request),
            header=self._get_header(request),
            cookie=self._get_cookie(request),
        )

    def _get_path(self, request: HttpRequest) -> dict:
        return request.resolver_match and request.resolver_match.kwargs or {}

    def _get_query(self, request: HttpRequest) -> ImmutableMultiDict:
        return ImmutableMultiDict(request.GET)

    def _get_header(self, request: HttpRequest) -> Headers:
        return Headers(request.headers.items())

    def _get_cookie(self, request: HttpRequest) -> ImmutableMultiDict:
        return ImmutableMultiDict(dict(request.COOKIES))

    def _get_full_url_pattern(self, request: HttpRequest) -> str:
        if request.resolver_match is None:
            path_pattern = request.path
        else:
            route = self.path_regex.sub(
                r'{\1}', request.resolver_match.route)
            # Delete start and end marker to allow concatenation.
            if route[:1] == "^":
                route = route[1:]
            if route[-1:] == "$":
                route = route[:-1]
            path_pattern = '/' + route

        current_scheme_host = request._current_scheme_host
        return urljoin(current_scheme_host, path_pattern)

    def _get_method(self, request: HttpRequest) -> str:
        return request.method.lower()

    def _get_body(self, request: HttpRequest) -> str:
        return request.body

    def _get_mimetype(self, request: HttpRequest) -> str:
        return request.content_type
