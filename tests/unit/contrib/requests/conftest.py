from io import BytesIO
from urllib.parse import parse_qs
from urllib.parse import urljoin

import pytest
from requests.models import Request
from requests.models import Response
from requests.structures import CaseInsensitiveDict
from urllib3.response import HTTPResponse


@pytest.fixture
def request_factory():
    schema = "http"
    server_name = "localhost"

    def create_request(
        method,
        path,
        subdomain=None,
        query_string="",
        content_type="application/json",
    ):
        base_url = "://".join([schema, server_name])
        url = urljoin(base_url, path)
        params = parse_qs(query_string)
        headers = {
            "Content-Type": content_type,
        }
        return Request(method, url, params=params, headers=headers)

    return create_request


@pytest.fixture
def response_factory():
    def create_response(
        data, status_code=200, content_type="application/json"
    ):
        fp = BytesIO(data)
        raw = HTTPResponse(fp, preload_content=False)
        resp = Response()
        resp.headers = CaseInsensitiveDict(
            {
                "Content-Type": content_type,
            }
        )
        resp.status_code = status_code
        resp.raw = raw
        return resp

    return create_response
