"""OpenAPI core wrappers module"""
import re

from openapi_core.wrappers.base import BaseOpenAPIRequest, BaseOpenAPIResponse

# https://docs.djangoproject.com/en/2.2/topics/http/urls/
#
# Currently unsupported are :
#   - nested arguments, e.g.: ^comments/(?:page-(?P<page_number>\d+)/)?$
#   - unnamed regex groups, e.g.: ^articles/([0-9]{4})/$
#   - multiple named parameters between a single pair of slashes e.g.: <page_slug>-<page_id>/edit/
#
# The regex matches everything, except a "/" until "<". Than only the name is exported, after which it matches ">" and
# everything until a "/".
PATH_PARAMETER_PATTERN = r'(?:[^\/]*?)<(?:(?:.*?:))*?(\w+)>(?:[^\/]*)'


class DjangoOpenAPIRequest(BaseOpenAPIRequest):
    path_regex = re.compile(PATH_PARAMETER_PATTERN)

    def __init__(self, request):
        self.request = request

    @property
    def host_url(self):
        """
        :return: The host with scheme as IRI.
        """
        return self.request._current_scheme_host

    @property
    def path(self):
        """
        :return: Requested path as unicode.
        """
        return self.request.path

    @property
    def method(self):
        """
        :return: The request method, in lowercase.
        """
        return self.request.method.lower()

    @property
    def path_pattern(self):
        """
        :return: The matched url pattern.
        """
        return self.path_regex.sub(r'{\1}', self.request.resolver_match.route)

    @property
    def parameters(self):
        """
        :return: A dictionary of all parameters.
        """
        return {
            'path': self.request.resolver_match.kwargs,
            'query': self.request.GET,
            'header': self.request.headers,
            'cookie': self.request.COOKIES,
        }

    @property
    def body(self):
        """
        :return: The request body, as string.
        """
        return self.request.body

    @property
    def mimetype(self):
        """
        :return: Like content type, but without parameters (eg, without charset, type etc.) and always lowercase.
        For example if the content type is "text/HTML; charset=utf-8" the mimetype would be "text/html".
        """
        return self.request.content_type


class DjangoOpenAPIResponse(BaseOpenAPIResponse):

    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        """
        :return: The response body, as string.
        """
        return self.response.content

    @property
    def status_code(self):
        """
        :return: The status code as integer.
        """
        return self.response.status_code

    @property
    def mimetype(self):
        """
        :return: Lowercase content type without charset.
        """
        return self.response["Content-Type"]
