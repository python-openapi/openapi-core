from aiohttp import web
from aiohttpproject.pets.views import PetPhotoView

routes = [
    web.view("/v1/pets/{petId}/photo", PetPhotoView),
]


def get_app(loop=None):
    app = web.Application(loop=loop)
    app.add_routes(routes)
    return app


app = get_app()
