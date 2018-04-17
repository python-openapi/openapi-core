"""OpenAPI X-Model extension factories module"""
from openapi_core.extensions.models.models import BaseModel


class ModelFactory(object):

    def create(self, properties, name=None):
        model = BaseModel
        if name is not None:
            model = type(name, (BaseModel, ), {})

        return model(**properties)
