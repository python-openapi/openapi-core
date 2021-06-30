from falcon import App

from falconproject.openapi import openapi_middleware
from falconproject.pets.resources import PetListResource, PetDetailResource

app = App(middleware=[openapi_middleware])

pet_list_resource = PetListResource()
pet_detail_resource = PetDetailResource()

app.add_route("/v1/pets", pet_list_resource)
app.add_route("/v1/pets/{petId}", pet_detail_resource)
