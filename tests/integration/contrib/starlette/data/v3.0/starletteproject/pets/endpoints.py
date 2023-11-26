from base64 import b64decode

from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.responses import StreamingResponse

OPENID_LOGO = b64decode(
    """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
)


async def pet_list_endpoint(request):
    assert request.scope["openapi"]
    assert not request.scope["openapi"].errors
    if request.method == "GET":
        assert request.scope["openapi"].parameters.query == {
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
        headers = {
            "X-Rate-Limit": "12",
        }
        return JSONResponse(response_dict, headers=headers)
    elif request.method == "POST":
        assert request.scope["openapi"].parameters.cookie == {
            "user": 1,
        }
        assert request.scope["openapi"].parameters.header == {
            "api-key": "12345",
        }
        assert request.scope["openapi"].body.__class__.__name__ == "PetCreate"
        assert request.scope["openapi"].body.name in ["Cat", "Bird"]
        if request.scope["openapi"].body.name == "Cat":
            assert (
                request.scope["openapi"].body.ears.__class__.__name__ == "Ears"
            )
            assert request.scope["openapi"].body.ears.healthy is True
        if request.scope["openapi"].body.name == "Bird":
            assert (
                request.scope["openapi"].body.wings.__class__.__name__
                == "Wings"
            )
            assert request.scope["openapi"].body.wings.healthy is True

        headers = {
            "X-Rate-Limit": "12",
        }
        return Response(status_code=201, headers=headers)


async def pet_detail_endpoint(request):
    assert request.scope["openapi"]
    assert not request.scope["openapi"].errors
    if request.method == "GET":
        assert request.scope["openapi"].parameters.path == {
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
        headers = {
            "X-Rate-Limit": "12",
        }
        return JSONResponse(response_dict, headers=headers)


async def pet_photo_endpoint(request):
    if request.method == "GET":
        contents = iter([OPENID_LOGO])
        return StreamingResponse(contents, media_type="image/gif")
    elif request.method == "POST":
        body = await request.body()
        assert body == OPENID_LOGO
        return Response(status_code=201)
