import pytest
import json

from openapi_core.shortcuts import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.wrappers.mock import MockRequest, MockResponse


class TestGetAndPost(object):

    get_object = [{
        "object_id": "random_id",
        "message": "test message"
    }]

    post_object = [{
        "message": "second message",
        "password": "fakepassword"
    }]
    spec_paths = [
        "data/v3.0/get_and_post.yaml",
    ]

    @pytest.mark.parametrize("response", post_object)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_post_object_success(self, factory, response, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        validator = RequestValidator(spec)
        request = MockRequest("http://www.example.com", "post",
                              "/object", data=json.dumps(response))

        result = validator.validate(request)
        assert not result.errors

    @pytest.mark.parametrize("response", get_object)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_post_object_failure(self, factory, response, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        validator = RequestValidator(spec)
        request = MockRequest("http://www.example.com", "post",
                              "/object", data=json.dumps(response))

        result = validator.validate(request)
        assert result.errors

    @pytest.mark.parametrize("response", get_object)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_get_object_success(self, factory, response, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        request = MockRequest("http://www.example.com", "get",
                              "/object/{objectId}")
        validator = ResponseValidator(spec)
        response = MockResponse(data=json.dumps(response))

        result = validator.validate(request, response)
        print(result.errors)
        assert not result.errors

    @pytest.mark.parametrize("response", post_object)
    @pytest.mark.parametrize("spec_path", spec_paths)
    def test_get_object_failure(self, factory, response, spec_path):
        spec_dict = factory.spec_from_file(spec_path)
        spec = create_spec(spec_dict)
        request = MockRequest("http://www.example.com", "get",
                              "/object/{objectId}")

        validator = ResponseValidator(spec)
        response = MockResponse(data=json.dumps(response))

        result = validator.validate(request, response)
        assert result.errors
