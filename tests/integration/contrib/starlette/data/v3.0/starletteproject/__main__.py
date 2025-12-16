from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route
from starletteproject.openapi import openapi
from starletteproject.pets.endpoints import pet_detail_endpoint
from starletteproject.pets.endpoints import pet_list_endpoint
from starletteproject.pets.endpoints import pet_photo_endpoint
from starletteproject.tags.endpoints import tag_list_endpoint

from openapi_core.contrib.starlette.middlewares import (
    StarletteOpenAPIMiddleware,
)

middleware = [
    Middleware(
        StarletteOpenAPIMiddleware,
        openapi=openapi,
    ),
]
middleware_skip_response = [
    Middleware(
        StarletteOpenAPIMiddleware,
        openapi=openapi,
        response_cls=None,
    ),
]

routes = [
    Route("/v1/pets", pet_list_endpoint, methods=["GET", "POST"]),
    Route("/v1/pets/{petId}", pet_detail_endpoint, methods=["GET", "POST"]),
    Route(
        "/v1/pets/{petId}/photo", pet_photo_endpoint, methods=["GET", "POST"]
    ),
    Route("/v1/tags", tag_list_endpoint, methods=["GET"]),
]

app = Starlette(
    debug=True,
    middleware=middleware,
    routes=routes,
)
app_skip_response = Starlette(
    debug=True,
    middleware=middleware_skip_response,
    routes=routes,
)
