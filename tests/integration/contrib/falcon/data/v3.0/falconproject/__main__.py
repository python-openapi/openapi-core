from falcon import App
from falconproject.openapi import openapi_middleware
from falconproject.pets.resources import PetDetailResource
from falconproject.pets.resources import PetListResource

app = App(middleware=[openapi_middleware])

pet_list_resource = PetListResource()
pet_detail_resource = PetDetailResource()

app.add_route("/v1/pets", pet_list_resource)
app.add_route("/v1/pets/{petId}", pet_detail_resource)
