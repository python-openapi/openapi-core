from json import loads as json_loads
from xml.etree.ElementTree import fromstring as xml_loads

from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.media_types.util import data_form_loads
from openapi_core.deserializing.media_types.util import plain_loads
from openapi_core.deserializing.media_types.util import urlencoded_form_loads

__all__ = ["media_type_deserializers_factory"]

media_type_deserializers: MediaTypeDeserializersDict = {
    "text/html": plain_loads,
    "text/plain": plain_loads,
    "application/json": json_loads,
    "application/vnd.api+json": json_loads,
    "application/xml": xml_loads,
    "application/xhtml+xml": xml_loads,
    "application/x-www-form-urlencoded": urlencoded_form_loads,
    "multipart/form-data": data_form_loads,
}

media_type_deserializers_factory = MediaTypeDeserializersFactory(
    media_type_deserializers=media_type_deserializers,
)
