import warnings
from typing import Any
from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.casters import SchemaCaster
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.styles.datatypes import DeserializerCallable


class StyleDeserializer:
    def __init__(
        self,
        style: str,
        explode: bool,
        name: str,
        schema: SchemaPath,
        caster: SchemaCaster,
        deserializer_callable: Optional[DeserializerCallable] = None,
    ):
        self.style = style
        self.explode = explode
        self.name = name
        self.schema = schema
        self.schema_type = schema.getkey("type", "")
        self.caster = caster
        self.deserializer_callable = deserializer_callable

    def deserialize(self, location: Mapping[str, Any]) -> Any:
        if self.deserializer_callable is None:
            warnings.warn(f"Unsupported {self.style} style")
            return location[self.name]

        try:
            value = self.deserializer_callable(
                self.explode, self.name, self.schema_type, location
            )
        except (ValueError, TypeError, AttributeError) as exc:
            raise DeserializeError(self.style, self.name) from exc

        try:
            return self.caster.cast(value)
        except (ValueError, TypeError, AttributeError) as exc:
            raise CastError(value, self.schema_type) from exc
