import pytest
from requests.models import Request, Response
from requests.structures import CaseInsensitiveDict
from six import BytesIO, b
from six.moves.urllib.parse import urljoin, parse_qs
from urllib3.response import HTTPResponse


@pytest.fixture
def request_factory():
    schema = 'http'
    server_name = 'localhost'

    def create_request(method, path, subdomain=None, query_string=''):
        base_url = '://'.join([schema, server_name])
        url = urljoin(base_url, path)
        params = parse_qs(query_string)
        headers = {
            'Content-Type': 'application/json',
        }
        return Request(method, url, params=params, headers=headers)
    return create_request


@pytest.fixture
def response_factory():
    def create_response(
            data, status_code=200, content_type='application/json'):
        fp = BytesIO(b(data))
        raw = HTTPResponse(fp, preload_content=False)
        resp = Response()
        resp.headers = CaseInsensitiveDict({
            'Content-Type': content_type,
        })
        resp.status_code = status_code
        resp.raw = raw
        return resp
    return create_response
