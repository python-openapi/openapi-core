from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.deserializers import (
    MediaTypeDeserializer,
)
from openapi_core.deserializing.media_types.deserializers import (
    MediaTypesDeserializer,
)
from openapi_core.deserializing.styles.datatypes import StyleDeserializersDict
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.validation.schemas.validators import SchemaValidator


class MediaTypeDeserializersFactory:
    def __init__(
        self,
        style_deserializers_factory: StyleDeserializersFactory,
        media_type_deserializers: Optional[MediaTypeDeserializersDict] = None,
    ):
        self.style_deserializers_factory = style_deserializers_factory
        if media_type_deserializers is None:
            media_type_deserializers = {}
        self.media_type_deserializers = media_type_deserializers

    @classmethod
    def from_schema_casters_factory(
        cls,
        schema_casters_factory: SchemaCastersFactory,
        style_deserializers: Optional[StyleDeserializersDict] = None,
        media_type_deserializers: Optional[MediaTypeDeserializersDict] = None,
    ) -> "MediaTypeDeserializersFactory":
        from openapi_core.deserializing.media_types import (
            media_type_deserializers as default_media_type_deserializers,
        )
        from openapi_core.deserializing.styles import (
            style_deserializers as default_style_deserializers,
        )

        style_deserializers_factory = StyleDeserializersFactory(
            schema_casters_factory,
            style_deserializers=style_deserializers
            or default_style_deserializers,
        )
        return cls(
            style_deserializers_factory,
            media_type_deserializers=media_type_deserializers
            or default_media_type_deserializers,
        )

    def create(
        self,
        mimetype: str,
        schema: Optional[SchemaPath] = None,
        schema_validator: Optional[SchemaValidator] = None,
        parameters: Optional[Mapping[str, str]] = None,
        encoding: Optional[SchemaPath] = None,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
    ) -> MediaTypeDeserializer:
        if parameters is None:
            parameters = {}
        if extra_media_type_deserializers is None:
            extra_media_type_deserializers = {}
        media_types_deserializer = MediaTypesDeserializer(
            self.media_type_deserializers,
            extra_media_type_deserializers,
        )

        # Create schema caster for urlencoded/multipart content types
        # Only create if both schema and schema_validator are provided
        schema_caster = None
        if (
            schema is not None
            and schema_validator is not None
            and (
                mimetype == "application/x-www-form-urlencoded"
                or mimetype.startswith("multipart")
            )
        ):
            schema_caster = (
                self.style_deserializers_factory.schema_casters_factory.create(
                    schema
                )
            )

        return MediaTypeDeserializer(
            self.style_deserializers_factory,
            media_types_deserializer,
            mimetype,
            schema=schema,
            schema_validator=schema_validator,
            schema_caster=schema_caster,
            encoding=encoding,
            **parameters,
        )
