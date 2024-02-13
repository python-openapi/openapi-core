from base64 import b64decode

from fastapi import APIRouter
from fastapi import Body
from fastapi import Request
from fastapi import Response
from fastapi import status

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

OPENID_LOGO = b64decode(
    """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
)


router = APIRouter(
    prefix="/v1/pets",
    tags=["pets"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def list_pets(request: Request, response: Response):
    assert request.scope["openapi"]
    assert not request.scope["openapi"].errors
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
    response.headers["X-Rate-Limit"] = "12"
    return {"data": data}


@router.post("")
async def create_pet(request: Request):
    assert request.scope["openapi"].parameters.cookie == {
        "user": 1,
    }
    assert request.scope["openapi"].parameters.header == {
        "api-key": "12345",
    }
    assert request.scope["openapi"].body.__class__.__name__ == "PetCreate"
    assert request.scope["openapi"].body.name in ["Cat", "Bird"]
    if request.scope["openapi"].body.name == "Cat":
        assert request.scope["openapi"].body.ears.__class__.__name__ == "Ears"
        assert request.scope["openapi"].body.ears.healthy is True
    if request.scope["openapi"].body.name == "Bird":
        assert (
            request.scope["openapi"].body.wings.__class__.__name__ == "Wings"
        )
        assert request.scope["openapi"].body.wings.healthy is True

    headers = {
        "X-Rate-Limit": "12",
    }
    return Response(status_code=status.HTTP_201_CREATED, headers=headers)


@router.get("/{petId}")
async def detail_pet(request: Request, response: Response):
    assert request.scope["openapi"]
    assert not request.scope["openapi"].errors
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
    response.headers["X-Rate-Limit"] = "12"
    return {
        "data": data,
    }


@router.get("/{petId}/photo")
async def download_pet_photo():
    return Response(content=OPENID_LOGO, media_type="image/gif")


@router.post("/{petId}/photo")
async def upload_pet_photo(
    image: Annotated[bytes, Body(media_type="image/jpg")],
):
    assert image == OPENID_LOGO
    return Response(status_code=status.HTTP_201_CREATED)
