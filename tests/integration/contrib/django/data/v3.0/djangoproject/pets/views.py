from base64 import b64decode

from django.http import FileResponse
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.views import APIView


class PetListView(APIView):
    def get(self, request):
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.query == {
            "page": 1,
            "limit": 12,
            "search": "",
        }
        data = [
            {
                "id": 12,
                "name": "Cat",
                "ears": {
                    "healthy": True,
                },
            },
        ]
        response_dict = {
            "data": data,
        }
        django_response = JsonResponse(response_dict)
        django_response["X-Rate-Limit"] = "12"

        return django_response

    def post(self, request):
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.cookie == {
            "user": 1,
        }
        assert request.openapi.parameters.header == {
            "api-key": "12345",
        }
        assert request.openapi.body.__class__.__name__ == "PetCreate"
        assert request.openapi.body.name in ["Cat", "Bird"]
        if request.openapi.body.name == "Cat":
            assert request.openapi.body.ears.__class__.__name__ == "Ears"
            assert request.openapi.body.ears.healthy is True
        if request.openapi.body.name == "Bird":
            assert request.openapi.body.wings.__class__.__name__ == "Wings"
            assert request.openapi.body.wings.healthy is True

        django_response = HttpResponse(status=201)
        django_response["X-Rate-Limit"] = "12"

        return django_response

    @staticmethod
    def get_extra_actions():
        return []


class PetDetailView(APIView):
    def get(self, request, petId):
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.path == {
            "petId": 12,
        }
        data = {
            "id": 12,
            "name": "Cat",
            "ears": {
                "healthy": True,
            },
        }
        response_dict = {
            "data": data,
        }
        django_response = JsonResponse(response_dict)
        django_response["X-Rate-Limit"] = "12"
        return django_response

    @staticmethod
    def get_extra_actions():
        return []


class PetPhotoView(APIView):
    OPENID_LOGO = b64decode(
        """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
    )

    def get(self, request, petId):
        assert request.openapi
        assert not request.openapi.errors
        assert request.openapi.parameters.path == {
            "petId": 12,
        }
        django_response = FileResponse(
            [self.OPENID_LOGO],
            content_type="image/gif",
        )
        return django_response

    def post(self, request, petId):
        assert request.openapi
        assert not request.openapi.errors

        # implement file upload here

        django_response = HttpResponse(status=201)

        return django_response

    @staticmethod
    def get_extra_actions():
        return []
