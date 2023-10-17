import re
from functools import partial
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.deserializing.styles.datatypes import DeserializerCallable
from openapi_core.deserializing.styles.datatypes import StyleDeserializersDict
from openapi_core.deserializing.styles.deserializers import StyleDeserializer
from openapi_core.deserializing.styles.util import split
from openapi_core.schema.parameters import get_explode
from openapi_core.schema.parameters import get_style


class StyleDeserializersFactory:
    def __init__(
        self,
        style_deserializers: Optional[StyleDeserializersDict] = None,
    ):
        if style_deserializers is None:
            style_deserializers = {}
        self.style_deserializers = style_deserializers

    def create(
        self, param_or_header: SchemaPath, name: Optional[str] = None
    ) -> StyleDeserializer:
        name = name or param_or_header["name"]
        style = get_style(param_or_header)
        explode = get_explode(param_or_header)
        schema = param_or_header / "schema"
        schema_type = schema.getkey("type", "")

        deserialize_callable = self.style_deserializers.get(style)
        return StyleDeserializer(
            style, explode, name, schema_type, deserialize_callable
        )
