from collections import defaultdict

from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.media_types.util import binary_loads
from openapi_core.deserializing.media_types.util import data_form_loads
from openapi_core.deserializing.media_types.util import json_loads
from openapi_core.deserializing.media_types.util import plain_loads
from openapi_core.deserializing.media_types.util import urlencoded_form_loads
from openapi_core.deserializing.media_types.util import xml_loads

__all__ = ["media_type_deserializers", "MediaTypeDeserializersFactory"]

media_type_deserializers: MediaTypeDeserializersDict = defaultdict(
    lambda: binary_loads,
    **{
        "text/html": plain_loads,
        "text/plain": plain_loads,
        "application/octet-stream": binary_loads,
        "application/json": json_loads,
        "application/vnd.api+json": json_loads,
        "application/xml": xml_loads,
        "application/xhtml+xml": xml_loads,
        "application/x-www-form-urlencoded": urlencoded_form_loads,
        "multipart/form-data": data_form_loads,
    }
)
