from starlette.applications import Starlette
from starlette.routing import Route
from starletteproject.pets.endpoints import pet_photo_endpoint

routes = [
    Route(
        "/v1/pets/{petId}/photo", pet_photo_endpoint, methods=["GET", "POST"]
    ),
]

app = Starlette(
    debug=True,
    routes=routes,
)
