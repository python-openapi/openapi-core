from json import loads

from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.media_types.util import data_form_loads
from openapi_core.deserializing.media_types.util import urlencoded_form_loads

__all__ = ["media_type_deserializers_factory"]

media_type_deserializers: MediaTypeDeserializersDict = {
    "application/json": loads,
    "application/x-www-form-urlencoded": urlencoded_form_loads,
    "multipart/form-data": data_form_loads,
}

media_type_deserializers_factory = MediaTypeDeserializersFactory(
    media_type_deserializers=media_type_deserializers,
)
