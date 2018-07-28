"""OpenAPI X-Model extension factories module"""
from openapi_core.extensions.models.models import BaseModel


class ModelFactory(object):

    base_class = BaseModel
    default_name = 'Model'

    def __init__(self, name=None):
        self.name = name or self.default_name

    def __call__(self, **properties):
        model_class = self._get_model_class(**properties)
        return model_class()

    def _get_model_class(self, **attrs):
        return type(self.name, (self.base_class, ), attrs)
