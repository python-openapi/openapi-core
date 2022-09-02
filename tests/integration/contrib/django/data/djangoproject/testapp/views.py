import yaml

from django.http import JsonResponse
from openapi_core import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.contrib.django import (
    DjangoOpenAPIRequest, DjangoOpenAPIResponse,
)
from rest_framework.views import APIView

from djangoproject import settings


class TestView(APIView):

    def get(self, request, pk):
        with open(settings.OPENAPI_SPEC_PATH) as file:
            spec_yaml = file.read()
        spec_dict = yaml.load(spec_yaml, yaml.FullLoader)
        spec = create_spec(spec_dict)

        openapi_request = DjangoOpenAPIRequest(request)

        request_validator = RequestValidator(spec)
        result = request_validator.validate(openapi_request)
        result.raise_for_errors()

        response_dict = {
            "test": "test_val",
        }
        django_response = JsonResponse(response_dict)

        openapi_response = DjangoOpenAPIResponse(django_response)
        validator = ResponseValidator(spec)
        result = validator.validate(openapi_request, openapi_response)
        result.raise_for_errors()

        return django_response

    @staticmethod
    def get_extra_actions():
        return []
