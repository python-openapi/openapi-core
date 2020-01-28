import pytest

from openapi_core.contrib.falcon.requests import FalconOpenAPIRequestFactory
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponseFactory
from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator


class TestFalconOpenAPIValidation(object):

    @pytest.fixture
    def spec(self, factory):
        specfile = 'contrib/falcon/data/v3.0/falcon_factory.yaml'
        return create_spec(factory.spec_from_file(specfile))

    def test_response_validator_path_pattern(self,
                                             spec,
                                             request_factory,
                                             response_factory):
        validator = ResponseValidator(spec)
        request = request_factory('GET', '/browse/12/', subdomain='kb')
        openapi_request = FalconOpenAPIRequestFactory.create(
            request, '/browse/12/')
        response = response_factory('{"data": "data"}', status_code=200)
        openapi_response = FalconOpenAPIResponseFactory.create(response)
        result = validator.validate(openapi_request, openapi_response)
        assert not result.errors

    def test_request_validator_path_pattern(self, spec, request_factory):
        validator = RequestValidator(spec)
        request = request_factory('GET', '/browse/12/', subdomain='kb')
        openapi_request = FalconOpenAPIRequestFactory.create(
            request, '/browse/12/')
        result = validator.validate(openapi_request)
        assert not result.errors
