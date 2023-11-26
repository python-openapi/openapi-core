from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.deserializing.styles.datatypes import StyleDeserializersDict
from openapi_core.deserializing.styles.deserializers import StyleDeserializer


class StyleDeserializersFactory:
    def __init__(
        self,
        style_deserializers: Optional[StyleDeserializersDict] = None,
    ):
        if style_deserializers is None:
            style_deserializers = {}
        self.style_deserializers = style_deserializers

    def create(
        self,
        style: str,
        explode: bool,
        schema: SchemaPath,
        name: str,
    ) -> StyleDeserializer:
        schema_type = schema.getkey("type", "")

        deserialize_callable = self.style_deserializers.get(style)
        return StyleDeserializer(
            style, explode, name, schema_type, deserialize_callable
        )
