from typing import Callable, Union
import warnings

from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)


class BaseMediaTypeDeserializer:

    def __init__(self, mimetype: str):
        self.mimetype = mimetype

    def __call__(self, value: str) -> Union[str, dict]:
        raise NotImplementedError


class UnsupportedMimetypeDeserializer(BaseMediaTypeDeserializer):

    def __call__(self, value: str) -> str:
        warnings.warn(f"Unsupported {self.mimetype} mimetype")
        return value


class CallableMediaTypeDeserializer(BaseMediaTypeDeserializer):

    def __init__(
        self,
        mimetype: str,
        deserializer_callable: Callable[[str], dict],
    ):
        self.mimetype = mimetype
        self.deserializer_callable = deserializer_callable

    def __call__(self, value: str) -> dict:
        try:
            return self.deserializer_callable(value)
        except (ValueError, TypeError, AttributeError):
            raise MediaTypeDeserializeError(self.mimetype, value)
