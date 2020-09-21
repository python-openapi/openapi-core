"""OpenAPI core contrib django requests module"""
import re

from six.moves.urllib.parse import urljoin

from openapi_core.validation.request.datatypes import (
    RequestParameters, OpenAPIRequest,
)

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


class DjangoOpenAPIRequestFactory(object):

    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    @classmethod
    def create(cls, request):
        method = request.method.lower()

        if request.resolver_match is None:
            path_pattern = request.path
        else:
            route = cls.path_regex.sub(
                r'{\1}', request.resolver_match.route)
            path_pattern = '/' + route

        path = request.resolver_match and request.resolver_match.kwargs or {}
        parameters = RequestParameters(
            path=path,
            query=request.GET,
            header=request.headers.items(),
            cookie=request.COOKIES,
        )
        full_url_pattern = urljoin(
            request._current_scheme_host, path_pattern)
        return OpenAPIRequest(
            full_url_pattern=full_url_pattern,
            method=method,
            parameters=parameters,
            body=request.data,
            mimetype=request.content_type,
        )
