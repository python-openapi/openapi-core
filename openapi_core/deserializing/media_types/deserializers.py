import warnings
from typing import Any
from typing import Callable

from openapi_core.deserializing.media_types.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)


class BaseMediaTypeDeserializer:
    def __init__(self, mimetype: str):
        self.mimetype = mimetype

    def __call__(self, value: Any) -> Any:
        raise NotImplementedError


class UnsupportedMimetypeDeserializer(BaseMediaTypeDeserializer):
    def __call__(self, value: Any) -> Any:
        warnings.warn(f"Unsupported {self.mimetype} mimetype")
        return value


class CallableMediaTypeDeserializer(BaseMediaTypeDeserializer):
    def __init__(
        self, mimetype: str, deserializer_callable: DeserializerCallable
    ):
        self.mimetype = mimetype
        self.deserializer_callable = deserializer_callable

    def __call__(self, value: Any) -> Any:
        try:
            return self.deserializer_callable(value)
        except (ValueError, TypeError, AttributeError):
            raise MediaTypeDeserializeError(self.mimetype, value)
