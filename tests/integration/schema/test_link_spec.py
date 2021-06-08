from openapi_core.shortcuts import create_spec


class TestLinkSpec:

    def test_no_param(self, factory):
        spec_dict = factory.spec_from_file("data/v3.0/links.yaml")
        spec = create_spec(spec_dict)
        resp = spec / 'paths#/status#get#responses#default'

        links = resp / 'links'
        assert len(links) == 1

        link = links / 'noParamLink'
        assert link['operationId'] == 'noParOp'
        assert 'server' not in link
        assert 'requestBody' not in link
        assert 'parameters' not in link

    def test_param(self, factory):
        spec_dict = factory.spec_from_file("data/v3.0/links.yaml")
        spec = create_spec(spec_dict)
        resp = spec / 'paths#/status/{resourceId}#get#responses#default'

        links = resp / 'links'
        assert len(links) == 1

        link = links / 'paramLink'
        assert link['operationId'] == 'paramOp'
        assert 'server' not in link
        assert link['requestBody'] == 'test'

        parameters = link['parameters']
        assert len(parameters) == 1

        param = parameters['opParam']
        assert param == '$request.path.resourceId'
