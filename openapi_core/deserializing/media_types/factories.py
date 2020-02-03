from openapi_core.schema.media_types.util import json_loads

from openapi_core.deserializing.media_types.deserializers import (
    PrimitiveDeserializer,
)


class MediaTypeDeserializersFactory(object):

    MEDIA_TYPE_DESERIALIZERS = {
        'application/json': json_loads,
    }

    def create(self, media_type):
        deserialize_callable = self.MEDIA_TYPE_DESERIALIZERS.get(
            media_type.mimetype, lambda x: x)
        return PrimitiveDeserializer(
            media_type.mimetype, deserialize_callable)
