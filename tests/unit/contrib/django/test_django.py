import pytest
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.django import DjangoOpenAPIRequest
from openapi_core.contrib.django import DjangoOpenAPIResponse
from openapi_core.datatypes import RequestParameters


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
            re_path("^object/(?P<pk>[^/.]+)/action/$", lambda d: None),
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
    def test_type_invalid(self):
        with pytest.raises(TypeError):
            DjangoOpenAPIRequest(None)

    def test_no_resolver(self, request_factory):
        data = {"test1": "test2"}
        request = request_factory.get("/admin/", data)

        openapi_request = DjangoOpenAPIRequest(request)

        assert openapi_request.parameters == RequestParameters(
            path={},
            query=ImmutableMultiDict([("test1", "test2")]),
            header=Headers({"Cookie": ""}),
            cookie={},
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.path_pattern is None
        assert openapi_request.body == b""
        assert openapi_request.content_type == request.content_type

    def test_simple(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/admin/")
        request.resolver_match = resolve(request.path)

        openapi_request = DjangoOpenAPIRequest(request)

        assert openapi_request.parameters == RequestParameters(
            path={},
            query={},
            header=Headers({"Cookie": ""}),
            cookie={},
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.path_pattern == request.path
        assert openapi_request.body == b""
        assert openapi_request.content_type == request.content_type

    def test_url_rule(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/admin/auth/group/1/")
        request.resolver_match = resolve(request.path)

        openapi_request = DjangoOpenAPIRequest(request)

        assert openapi_request.parameters == RequestParameters(
            path={"object_id": "1"},
            query={},
            header=Headers({"Cookie": ""}),
            cookie={},
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.path_pattern == "/admin/auth/group/{object_id}/"
        assert openapi_request.body == b""
        assert openapi_request.content_type == request.content_type

    def test_url_regexp_pattern(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/test/test-regexp/")
        request.resolver_match = resolve(request.path)

        openapi_request = DjangoOpenAPIRequest(request)

        assert openapi_request.parameters == RequestParameters(
            path={},
            query={},
            header=Headers({"Cookie": ""}),
            cookie={},
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.path_pattern == request.path
        assert openapi_request.body == b""
        assert openapi_request.content_type == request.content_type

    def test_drf_default_value_pattern(self, request_factory):
        from django.urls import resolve

        request = request_factory.get("/object/123/action/")
        request.resolver_match = resolve(request.path)

        openapi_request = DjangoOpenAPIRequest(request)

        assert openapi_request.parameters == RequestParameters(
            path={"pk": "123"},
            query={},
            header=Headers({"Cookie": ""}),
            cookie={},
        )
        assert openapi_request.method == request.method.lower()
        assert openapi_request.host_url == request._current_scheme_host
        assert openapi_request.path == request.path
        assert openapi_request.path_pattern == "/object/{pk}/action/"
        assert openapi_request.body == b""
        assert openapi_request.content_type == request.content_type


class TestDjangoOpenAPIResponse(BaseTestDjango):
    def test_type_invalid(self):
        with pytest.raises(TypeError):
            DjangoOpenAPIResponse(None)

    def test_stream_response(self, response_factory):
        response = response_factory()
        response.writelines(["foo\n", "bar\n", "baz\n"])

        openapi_response = DjangoOpenAPIResponse(response)

        assert openapi_response.data == b"foo\nbar\nbaz\n"
        assert openapi_response.status_code == response.status_code
        assert openapi_response.content_type == response["Content-Type"]

    def test_redirect_response(self, response_factory):
        data = b"/redirected/"
        response = response_factory(data, status_code=302)

        openapi_response = DjangoOpenAPIResponse(response)

        assert openapi_response.data == data
        assert openapi_response.status_code == response.status_code
        assert openapi_response.content_type == response["Content-Type"]
