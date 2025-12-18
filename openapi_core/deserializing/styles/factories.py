from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.styles.datatypes import StyleDeserializersDict
from openapi_core.deserializing.styles.deserializers import StyleDeserializer


class StyleDeserializersFactory:
    def __init__(
        self,
        schema_casters_factory: SchemaCastersFactory,
        style_deserializers: Optional[StyleDeserializersDict] = None,
    ):
        self.schema_casters_factory = schema_casters_factory
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
        deserialize_callable = self.style_deserializers.get(style)
        caster = self.schema_casters_factory.create(schema)
        return StyleDeserializer(
            style, explode, name, schema, caster, deserialize_callable
        )
