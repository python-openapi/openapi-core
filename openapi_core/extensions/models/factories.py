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


class DictFactory:

    base_class = dict

    def create(self, fields: Iterable[Field]) -> Type[Dict[Any, Any]]:
        return self.base_class


class DataClassFactory(DictFactory):
    def create(
        self,
        fields: Iterable[Field],
        name: str = "Model",
    ) -> Type[Any]:
        return make_dataclass(name, fields, frozen=True)


class ModelClassImporter(DataClassFactory):
    def create(
        self,
        fields: Iterable[Field],
        name: str = "Model",
        model: Optional[str] = None,
    ) -> Any:
        if model is None:
            return super().create(fields, name=name)

        model_class = self._get_class(model)
        if model_class is not None:
            return model_class

        return super().create(fields, name=model)

    def _get_class(self, model_class_path: str) -> Optional[object]:
        try:
            return locate(model_class_path)
        except ErrorDuringImport:
            return None
