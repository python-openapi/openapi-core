"""OpenAPI core contrib django module"""
from openapi_core.contrib.django.requests import DjangoOpenAPIRequestFactory
from openapi_core.contrib.django.responses import DjangoOpenAPIResponseFactory

DjangoOpenAPIRequest = DjangoOpenAPIRequestFactory().create
DjangoOpenAPIResponse = DjangoOpenAPIResponseFactory().create

__all__ = [
    "DjangoOpenAPIRequestFactory",
    "DjangoOpenAPIResponseFactory",
    "DjangoOpenAPIRequest",
    "DjangoOpenAPIResponse",
]
