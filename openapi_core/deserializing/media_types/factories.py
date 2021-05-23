from json import loads
from typing import Callable, Dict, Optional

from openapi_core.deserializing.media_types.util import (
    urlencoded_form_loads, data_form_loads,
)

from openapi_core.deserializing.media_types.deserializers import (
    BaseMediaTypeDeserializer, CallableMediaTypeDeserializer,
    UnsupportedMimetypeDeserializer,
)


class MediaTypeDeserializersFactory:

    MEDIA_TYPE_DESERIALIZERS: Dict[str, Callable[[str], dict]] = {
        'application/json': loads,
        'application/x-www-form-urlencoded': urlencoded_form_loads,
        'multipart/form-data': data_form_loads,
    }

    def __init__(
        self,
        custom_deserializers: Optional[
            Dict[str, Callable[[str], dict]]
        ] = None,
    ):
        if custom_deserializers is None:
            custom_deserializers = {}
        self.custom_deserializers = custom_deserializers

    def create(self, mimetype: str) -> BaseMediaTypeDeserializer:
        deserialize_callable = self.get_deserializer_callable(
            mimetype)

        if deserialize_callable is None:
            return UnsupportedMimetypeDeserializer(mimetype)

        return CallableMediaTypeDeserializer(
            mimetype, deserialize_callable)

    def get_deserializer_callable(
        self,
        mimetype: str,
    ) -> Optional[Callable[[str], dict]]:
        if mimetype in self.custom_deserializers:
            return self.custom_deserializers[mimetype]
        return self.MEDIA_TYPE_DESERIALIZERS.get(mimetype)
