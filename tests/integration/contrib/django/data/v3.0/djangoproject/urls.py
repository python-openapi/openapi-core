"""djangotest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include
from django.urls import path
from djangoproject.pets.views import PetDetailView
from djangoproject.pets.views import PetListView
from djangoproject.pets.views import PetPhotoView
from djangoproject.status.views import get_status
from djangoproject.tags.views import TagListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    path(
        "v1/pets",
        PetListView.as_view(),
        name="pet_list_view",
    ),
    path(
        "v1/pets/<int:petId>",
        PetDetailView.as_view(),
        name="pet_detail_view",
    ),
    path(
        "v1/pets/<int:petId>/photo",
        PetPhotoView.as_view(),
        name="pet_photo_view",
    ),
    path(
        "v1/tags",
        TagListView.as_view(),
        name="tag_list_view",
    ),
    path(
        "status",
        get_status,
        name="get_status_view",
    ),
]
