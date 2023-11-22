from flask import Flask
from flaskproject.openapi import openapi
from flaskproject.pets.views import PetPhotoView

app = Flask(__name__)

app.add_url_rule(
    "/v1/pets/<int:petId>/photo",
    view_func=PetPhotoView.as_view("pet_photo", openapi),
    methods=["GET", "POST"],
)
