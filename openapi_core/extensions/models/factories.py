"""OpenAPI X-Model extension factories module"""
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from openapi_core.extensions.models.models import Model


class ModelClassFactory:

    base_class = Model

    def create(self, name: str) -> Type[Model]:
        return type(name, (self.base_class,), {})


class ModelFactory:
    def __init__(
        self, model_class_factory: Optional[ModelClassFactory] = None
    ):
        self.model_class_factory = model_class_factory or ModelClassFactory()

    def create(
        self, properties: Optional[Dict[str, Any]], name: Optional[str] = None
    ) -> Model:
        name = name or "Model"

        model_class = self._create_class(name)
        return model_class(properties)

    def _create_class(self, name: str) -> Type[Model]:
        return self.model_class_factory.create(name)
