"""OpenAPI core contrib django compat module"""
from openapi_core.contrib.django.backports import (
    HttpHeaders, request_current_scheme_host,
)


def get_request_headers(req):
    # in Django 1 headers is not defined
    return req.headers if hasattr(req, 'headers') else \
        HttpHeaders(req.META)


def get_response_headers(resp):
    # in Django 2 headers is not defined
    return resp.headers if hasattr(resp, 'headers') else \
        dict(resp._headers.values())


def get_current_scheme_host(req):
    # in Django 1 _current_scheme_host is not defined
    return req._current_scheme_host if hasattr(req, '_current_scheme_host') \
        else request_current_scheme_host(req)
