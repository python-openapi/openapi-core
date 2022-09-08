from json import loads
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional

from openapi_core.deserializing.media_types.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.media_types.deserializers import (
    BaseMediaTypeDeserializer,
)
from openapi_core.deserializing.media_types.deserializers import (
    CallableMediaTypeDeserializer,
)
from openapi_core.deserializing.media_types.deserializers import (
    UnsupportedMimetypeDeserializer,
)
from openapi_core.deserializing.media_types.util import data_form_loads
from openapi_core.deserializing.media_types.util import urlencoded_form_loads


class MediaTypeDeserializersFactory:

    MEDIA_TYPE_DESERIALIZERS: Dict[str, DeserializerCallable] = {
        "application/json": loads,
        "application/x-www-form-urlencoded": urlencoded_form_loads,
        "multipart/form-data": data_form_loads,
    }

    def __init__(
        self,
        custom_deserializers: Optional[Dict[str, DeserializerCallable]] = None,
    ):
        if custom_deserializers is None:
            custom_deserializers = {}
        self.custom_deserializers = custom_deserializers

    def create(self, mimetype: str) -> BaseMediaTypeDeserializer:
        deserialize_callable = self.get_deserializer_callable(mimetype)

        if deserialize_callable is None:
            return UnsupportedMimetypeDeserializer(mimetype)

        return CallableMediaTypeDeserializer(mimetype, deserialize_callable)

    def get_deserializer_callable(
        self, mimetype: str
    ) -> Optional[DeserializerCallable]:
        if mimetype in self.custom_deserializers:
            return self.custom_deserializers[mimetype]
        return self.MEDIA_TYPE_DESERIALIZERS.get(mimetype)
