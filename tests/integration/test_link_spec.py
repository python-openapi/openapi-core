from openapi_core.shortcuts import create_spec


class TestLinkSpec(object):

    def test_no_param(self, factory):
        spec_dict = factory.spec_from_file("data/v3.0/links.yaml")
        spec = create_spec(spec_dict)
        resp = spec['/status']['get'].get_response()

        assert len(resp.links) == 1

        link = resp.links['noParamLink']

        assert link.operationId == 'noParOp'
        assert link.server is None
        assert link.request_body is None
        assert len(link.parameters) == 0

    def test_param(self, factory):
        spec_dict = factory.spec_from_file("data/v3.0/links.yaml")
        spec = create_spec(spec_dict)
        resp = spec['/status/{resourceId}']['get'].get_response()

        assert len(resp.links) == 1

        link = resp.links['paramLink']

        assert link.operationId == 'paramOp'
        assert link.server is None
        assert link.request_body == 'test'
        assert len(link.parameters) == 1

        param = link.parameters['opParam']

        assert param == '$request.path.resourceId'
