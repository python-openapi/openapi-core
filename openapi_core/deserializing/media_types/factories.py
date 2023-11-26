from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.deserializers import (
    MediaTypeDeserializer,
)
from openapi_core.deserializing.media_types.deserializers import (
    MediaTypesDeserializer,
)
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)


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

    def create(
        self,
        mimetype: str,
        schema: Optional[SchemaPath] = None,
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

        return MediaTypeDeserializer(
            self.style_deserializers_factory,
            media_types_deserializer,
            mimetype,
            schema=schema,
            encoding=encoding,
            **parameters,
        )
