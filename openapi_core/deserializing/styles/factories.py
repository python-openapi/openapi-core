import re
from functools import partial
from typing import Dict

from jsonschema_path import SchemaPath

from openapi_core.deserializing.styles.datatypes import DeserializerCallable
from openapi_core.deserializing.styles.deserializers import (
    CallableStyleDeserializer,
)
from openapi_core.deserializing.styles.util import split
from openapi_core.schema.parameters import get_style


class StyleDeserializersFactory:
    STYLE_DESERIALIZERS: Dict[str, DeserializerCallable] = {
        "form": partial(split, separator=","),
        "simple": partial(split, separator=","),
        "spaceDelimited": partial(split, separator=" "),
        "pipeDelimited": partial(split, separator="|"),
        "deepObject": partial(re.split, pattern=r"\[|\]"),
    }

    def create(self, param_or_header: SchemaPath) -> CallableStyleDeserializer:
        style = get_style(param_or_header)

        deserialize_callable = self.STYLE_DESERIALIZERS.get(style)
        return CallableStyleDeserializer(
            param_or_header, style, deserialize_callable
        )
