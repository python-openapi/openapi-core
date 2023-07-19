import warnings
from typing import Any
from typing import Optional
from xml.etree.ElementTree import ParseError

from openapi_core.deserializing.media_types.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)


class CallableMediaTypeDeserializer:
    def __init__(
        self,
        mimetype: str,
        deserializer_callable: Optional[DeserializerCallable] = None,
    ):
        self.mimetype = mimetype
        self.deserializer_callable = deserializer_callable

    def deserialize(self, value: Any) -> Any:
        if self.deserializer_callable is None:
            warnings.warn(f"Unsupported {self.mimetype} mimetype")
            return value

        try:
            return self.deserializer_callable(value)
        except (ParseError, ValueError, TypeError, AttributeError):
            raise MediaTypeDeserializeError(self.mimetype, value)
