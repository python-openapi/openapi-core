"""OpenAPI X-Model extension models module"""
from typing import Any
from typing import Dict
from typing import Optional


class BaseModel:
    """Base class for OpenAPI X-Model."""

    @property
    def __dict__(self) -> Dict[Any, Any]:  # type: ignore
        raise NotImplementedError


class Model(BaseModel):
    """Model class for OpenAPI X-Model."""

    def __init__(self, properties: Optional[Dict[str, Any]] = None):
        self.__properties = properties or {}

    @property
    def __dict__(self) -> Dict[Any, Any]:  # type: ignore
        return self.__properties

    def __getattr__(self, name: str) -> Any:
        if name not in self.__properties:
            raise AttributeError

        return self.__properties[name]
