import mock
import pytest

from openapi_core.schema.request_bodies.models import RequestBody


class TestRequestBodies(object):

    @pytest.fixture
    def request_body(self):
        content = {
            'application/json': mock.sentinel.application_json,
            'text/csv': mock.sentinel.text_csv,
        }
        return RequestBody(content)

    @property
    def test_iteritems(self, request_body):
        for mimetype in request_body.content.keys():
            assert request_body[mimetype] ==\
                request_body.content[mimetype]
