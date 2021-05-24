import pytest


class TestDjangoRESTFrameworkAPIView:

    @pytest.fixture
    def api_request_factory(self):
        from rest_framework.test import APIRequestFactory
        return APIRequestFactory()

    def test_get(self, api_request_factory):
        from djangoproject.testapp.views import TestView
        view = TestView.as_view()
        request = api_request_factory.get('/test/4')

        response = view(request, pk='4')

        assert response.content == b'{"test": "test_val"}'
