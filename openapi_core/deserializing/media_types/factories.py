from openapi_core.deserializing.media_types.util import json_loads

from openapi_core.deserializing.media_types.deserializers import (
    PrimitiveDeserializer,
)


class MediaTypeDeserializersFactory(object):

    MEDIA_TYPE_DESERIALIZERS = {
        'application/json': json_loads,
    }

    def __init__(self, custom_deserializers=None):
        if custom_deserializers is None:
            custom_deserializers = {}
        self.custom_deserializers = custom_deserializers

    def create(self, media_type):
        deserialize_callable = self.get_deserializer_callable(
            media_type.mimetype)
        return PrimitiveDeserializer(
            media_type.mimetype, deserialize_callable)

    def get_deserializer_callable(self, mimetype):
        if mimetype in self.custom_deserializers:
            return self.custom_deserializers[mimetype]
        return self.MEDIA_TYPE_DESERIALIZERS.get(mimetype, lambda x: x)
