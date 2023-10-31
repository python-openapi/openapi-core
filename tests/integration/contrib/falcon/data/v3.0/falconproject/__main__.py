from falcon import App
from falcon import media
from falconproject.openapi import openapi_middleware
from falconproject.pets.resources import PetDetailResource
from falconproject.pets.resources import PetListResource
from falconproject.pets.resources import PetPhotoResource

extra_handlers = {
    "application/vnd.api+json": media.JSONHandler(),
}

app = App(middleware=[openapi_middleware])

app.req_options.media_handlers.update(extra_handlers)
app.resp_options.media_handlers.update(extra_handlers)

pet_list_resource = PetListResource()
pet_detail_resource = PetDetailResource()
pet_photo_resource = PetPhotoResource()

app.add_route("/v1/pets", pet_list_resource)
app.add_route("/v1/pets/{petId}", pet_detail_resource)
app.add_route("/v1/pets/{petId}/photo", pet_photo_resource)
