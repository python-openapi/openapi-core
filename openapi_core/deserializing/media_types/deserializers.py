import warnings

from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)


class BaseMediaTypeDeserializer:
    def __init__(self, mimetype):
        self.mimetype = mimetype

    def __call__(self, value):
        raise NotImplementedError


class UnsupportedMimetypeDeserializer(BaseMediaTypeDeserializer):
    def __call__(self, value):
        warnings.warn(f"Unsupported {self.mimetype} mimetype")
        return value


class CallableMediaTypeDeserializer(BaseMediaTypeDeserializer):
    def __init__(self, mimetype, deserializer_callable):
        self.mimetype = mimetype
        self.deserializer_callable = deserializer_callable

    def __call__(self, value):
        try:
            return self.deserializer_callable(value)
        except (ValueError, TypeError, AttributeError):
            raise MediaTypeDeserializeError(self.mimetype, value)
