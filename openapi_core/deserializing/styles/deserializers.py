import warnings
from typing import Any
from typing import Mapping
from typing import Optional

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.styles.datatypes import DeserializerCallable


class StyleDeserializer:
    def __init__(
        self,
        style: str,
        explode: bool,
        name: str,
        schema_type: str,
        deserializer_callable: Optional[DeserializerCallable] = None,
    ):
        self.style = style
        self.explode = explode
        self.name = name
        self.schema_type = schema_type
        self.deserializer_callable = deserializer_callable

    def deserialize(self, location: Mapping[str, Any]) -> Any:
        if self.deserializer_callable is None:
            warnings.warn(f"Unsupported {self.style} style")
            return location[self.name]

        try:
            return self.deserializer_callable(
                self.explode, self.name, self.schema_type, location
            )
        except (ValueError, TypeError, AttributeError):
            raise DeserializeError(self.style, self.name)
