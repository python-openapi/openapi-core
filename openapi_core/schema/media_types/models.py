"""OpenAPI core media types models module"""
from collections import defaultdict

from openapi_core.schema.media_types.exceptions import InvalidMediaTypeValue
from openapi_core.schema.media_types.util import json_loads
from openapi_core.casting.schemas.exceptions import CastError


MEDIA_TYPE_DESERIALIZERS = {
    'application/json': json_loads,
}


class MediaType(object):
    """Represents an OpenAPI MediaType."""

    def __init__(self, mimetype, schema=None, example=None):
        self.mimetype = mimetype
        self.schema = schema
        self.example = example

    def get_deserializer_mapping(self):
        mapping = MEDIA_TYPE_DESERIALIZERS.copy()
        return defaultdict(lambda: lambda x: x, mapping)

    def get_dererializer(self):
        mapping = self.get_deserializer_mapping()
        return mapping[self.mimetype]

    def deserialize(self, value):
        deserializer = self.get_dererializer()
        return deserializer(value)

    def cast(self, value):
        if not self.schema:
            return value

        try:
            deserialized = self.deserialize(value)
        except ValueError as exc:
            raise InvalidMediaTypeValue(exc)

        try:
            return self.schema.cast(deserialized)
        except CastError as exc:
            raise InvalidMediaTypeValue(exc)
