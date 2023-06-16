from typing import Optional

from openapi_core.deserializing.media_types.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.deserializers import (
    CallableMediaTypeDeserializer,
)


class MediaTypeDeserializersFactory:
    def __init__(
        self,
        media_type_deserializers: Optional[MediaTypeDeserializersDict] = None,
    ):
        if media_type_deserializers is None:
            media_type_deserializers = {}
        self.media_type_deserializers = media_type_deserializers

    def create(
        self,
        mimetype: str,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
    ) -> CallableMediaTypeDeserializer:
        if extra_media_type_deserializers is None:
            extra_media_type_deserializers = {}
        deserialize_callable = self.get_deserializer_callable(
            mimetype,
            extra_media_type_deserializers=extra_media_type_deserializers,
        )

        return CallableMediaTypeDeserializer(mimetype, deserialize_callable)

    def get_deserializer_callable(
        self,
        mimetype: str,
        extra_media_type_deserializers: MediaTypeDeserializersDict,
    ) -> Optional[DeserializerCallable]:
        if mimetype in extra_media_type_deserializers:
            return extra_media_type_deserializers[mimetype]
        return self.media_type_deserializers.get(mimetype)
