from base64 import b64decode
from json import dumps

from falcon.constants import MEDIA_JPEG
from falcon.constants import MEDIA_JSON
from falcon.status_codes import HTTP_200
from falcon.status_codes import HTTP_201


class PetListResource:
    def on_get(self, request, response):
        assert request.context.openapi
        assert not request.context.openapi.errors
        if "ids" in request.params:
            assert request.context.openapi.parameters.query == {
                "page": 1,
                "limit": 2,
                "search": "",
                "ids": [1, 2],
            }
        else:
            assert request.context.openapi.parameters.query == {
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
        response.status = HTTP_200
        response.content_type = MEDIA_JSON
        response.text = dumps({"data": data})
        response.set_header("X-Rate-Limit", "12")

    def on_post(self, request, response):
        assert request.context.openapi
        assert not request.context.openapi.errors
        assert request.context.openapi.parameters.cookie == {
            "user": 1,
        }
        assert request.context.openapi.parameters.header == {
            "api-key": "12345",
        }
        assert request.context.openapi.body.__class__.__name__ == "PetCreate"
        assert request.context.openapi.body.name in ["Cat", "Bird"]
        if request.context.openapi.body.name == "Cat":
            assert (
                request.context.openapi.body.ears.__class__.__name__ == "Ears"
            )
            assert request.context.openapi.body.ears.healthy is True
        if request.context.openapi.body.name == "Bird":
            assert (
                request.context.openapi.body.wings.__class__.__name__
                == "Wings"
            )
            assert request.context.openapi.body.wings.healthy is True

        response.status = HTTP_201
        response.set_header("X-Rate-Limit", "12")


class PetDetailResource:
    def on_get(self, request, response, petId=None):
        assert petId == "12"
        assert request.context.openapi
        assert not request.context.openapi.errors
        assert request.context.openapi.parameters.path == {
            "petId": 12,
        }
        data = {
            "id": 12,
            "name": "Cat",
            "ears": {
                "healthy": True,
            },
        }
        response.status = HTTP_200
        response.content_type = MEDIA_JSON
        response.text = dumps({"data": data})
        response.set_header("X-Rate-Limit", "12")


class PetPhotoResource:
    OPENID_LOGO = b64decode(
        """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
    )

    def on_get(self, request, response, petId=None):
        response.content_type = MEDIA_JPEG
        response.stream = [self.OPENID_LOGO]

    def on_post(self, request, response, petId=None):
        data = request.stream.read()
        assert data == self.OPENID_LOGO
        response.status = HTTP_201
