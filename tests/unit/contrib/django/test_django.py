import pytest
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.django import DjangoOpenAPIRequest
from openapi_core.contrib.django import DjangoOpenAPIResponse
from openapi_core.validation.request.datatypes import RequestParameters


class BaseTestDjango:
    @pytest.fixture(autouse=True, scope="module")
    def django_settings(self):
        import django
        from django.conf import settings
        from django.contrib import admin
        from django.urls import path
        from django.urls import re_path

        if settings.configured:
            from django.utils.functional import empty

            settings._wrapped = empty

        settings.configure(
            SECRET_KEY="secretkey",
            ALLOWED_HOSTS=[
                "testserver",
            ],
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.messages",
                "django.contrib.sessions",
            ],
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
            ],
        )
        django.setup()
        settings.ROOT_URLCONF = (
            path("admin/", admin.site.urls),
            re_path("^test/test-regexp/$", lambda d: None),
        )

    @pytest.fixture
    def request_factory(self):
        from django.test.client import RequestFactory

        return RequestFactory()

    @pytest.fixture
    def response_factory(self):
        from django.http import HttpResponse

        def create(content=b"", status_code=None):
            return HttpResponse(content, status=status_code)

        return create


class TestDjangoOpenAPIRequest(BaseTestDjango):
    def test_no_resolver(self, request_factory):
        data = {"test1": "test2"}
        request = request_factory.get("/admin/", data)

        openapi_request = DjangoOpenAPIRequest(request)

        path = {}
        query = ImmutableMultiDict(
            [
                ("test1", "test2"),
            ]
        )
        headers = Headers(
            {
                "Cookie": "",
            }
        )
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.body == ""
        assert openapi_request.mimetype == request.content_type

    def test_simple(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/admin/")
        request.resolver_match = resolve("/admin/")

        openapi_request = DjangoOpenAPIRequest(request)

        path = {}
        query = {}
        headers = Headers(
            {
                "Cookie": "",
            }
        )
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.body == ""
        assert openapi_request.mimetype == request.content_type

    def test_url_rule(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/admin/auth/group/1/")
        request.resolver_match = resolve("/admin/auth/group/1/")

        openapi_request = DjangoOpenAPIRequest(request)

        path = {
            "object_id": "1",
        }
        query = {}
        headers = Headers(
            {
                "Cookie": "",
            }
        )
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.path_pattern == "/admin/auth/group/{object_id}/"
        assert openapi_request.body == ""
        assert openapi_request.mimetype == request.content_type

    def test_url_regexp_pattern(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/test/test-regexp/")
        request.resolver_match = resolve("/test/test-regexp/")

        openapi_request = DjangoOpenAPIRequest(request)

        path = {}
        query = {}
        headers = Headers(
            {
                "Cookie": "",
            }
        )
        cookies = {}
        assert openapi_request.parameters == RequestParameters(
            path=path,
            query=query,
            header=headers,
            cookie=cookies,
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == "/test/test-regexp/"
        assert openapi_request.body == ""
        assert openapi_request.mimetype == request.content_type


class TestDjangoOpenAPIResponse(BaseTestDjango):
    def test_stream_response(self, response_factory):
        response = response_factory()
        response.writelines(["foo\n", "bar\n", "baz\n"])

        openapi_response = DjangoOpenAPIResponse(response)

        assert openapi_response.data == "foo\nbar\nbaz\n"
        assert openapi_response.status_code == response.status_code
        assert openapi_response.mimetype == response["Content-Type"]

    def test_redirect_response(self, response_factory):
        data = "/redirected/"
        response = response_factory(data, status_code=302)

        openapi_response = DjangoOpenAPIResponse(response)

        assert openapi_response.data == data
        assert openapi_response.status_code == response.status_code
        assert openapi_response.mimetype == response["Content-Type"]
