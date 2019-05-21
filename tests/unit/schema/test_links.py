import mock
import pytest

from openapi_core.schema.links.models import Link
from openapi_core.schema.servers.models import Server


class TestLinks(object):

    @pytest.fixture
    def link_factory(self):
        def link_factory(request_body, server):
            parameters = {
                'par1': mock.sentinel.par1,
                'par2': mock.sentinel.par2,
            }
            return Link(
                'op_id',
                parameters,
                request_body,
                'Test link',
                server
            )
        return link_factory

    servers = [
        None,
        Server("https://bad.remote.domain.net/"),
        Server("http://localhost")
    ]

    request_body_list = [
        None,
        "request",
        '{"request": "value", "opt": 2}',
        {"request": "value", "opt": 2}
    ]

    @pytest.mark.parametrize("server", servers)
    @pytest.mark.parametrize("request_body", request_body_list)
    def test_iteritems(self, link_factory, request_body, server):
        link = link_factory(request_body, server)
        for par_name in link.parameters.keys():
            assert link[par_name] == link.parameters[par_name]
