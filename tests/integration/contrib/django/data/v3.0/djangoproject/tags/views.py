from django.http import HttpResponse
from rest_framework.views import APIView


class TagListView(APIView):
    def get(self, request):
        assert request.openapi
        assert not request.openapi.errors
        return HttpResponse("success")

    @staticmethod
    def get_extra_actions():
        return []
