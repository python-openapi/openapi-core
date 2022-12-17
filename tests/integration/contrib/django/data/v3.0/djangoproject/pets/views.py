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
