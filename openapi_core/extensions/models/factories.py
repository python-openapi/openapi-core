"""OpenAPI X-Model extension factories module"""
from dataclasses import make_dataclass
from pydoc import ErrorDuringImport
from pydoc import locate
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Type

from openapi_core.extensions.models.types import Field
from openapi_core.spec import Spec


class DictFactory:

    base_class = dict

    def create(
        self, schema: Spec, fields: Iterable[Field]
    ) -> Type[Dict[Any, Any]]:
        return self.base_class


class ModelFactory(DictFactory):
    def create(
        self,
        schema: Spec,
        fields: Iterable[Field],
    ) -> Type[Any]:
        name = schema.getkey("x-model")
        if name is None:
            return super().create(schema, fields)

        return make_dataclass(name, fields, frozen=True)


class ModelPathFactory(ModelFactory):
    def create(
        self,
        schema: Spec,
        fields: Iterable[Field],
    ) -> Any:
        model_class_path = schema.getkey("x-model-path")
        if model_class_path is None:
            return super().create(schema, fields)

        return locate(model_class_path)
