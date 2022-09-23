import re
from functools import partial
from typing import Dict

from openapi_core.deserializing.parameters.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.parameters.deserializers import (
    BaseParameterDeserializer,
)
from openapi_core.deserializing.parameters.deserializers import (
    CallableParameterDeserializer,
)
from openapi_core.deserializing.parameters.deserializers import (
    UnsupportedStyleDeserializer,
)
from openapi_core.deserializing.parameters.util import split
from openapi_core.schema.parameters import get_style
from openapi_core.spec import Spec


class ParameterDeserializersFactory:

    PARAMETER_STYLE_DESERIALIZERS: Dict[str, DeserializerCallable] = {
        "form": partial(split, separator=","),
        "simple": partial(split, separator=","),
        "spaceDelimited": partial(split, separator=" "),
        "pipeDelimited": partial(split, separator="|"),
        "deepObject": partial(re.split, pattern=r"\[|\]"),
    }

    def create(self, param_or_header: Spec) -> BaseParameterDeserializer:
        style = get_style(param_or_header)

        if style not in self.PARAMETER_STYLE_DESERIALIZERS:
            return UnsupportedStyleDeserializer(param_or_header, style)

        deserialize_callable = self.PARAMETER_STYLE_DESERIALIZERS[style]
        return CallableParameterDeserializer(
            param_or_header, style, deserialize_callable
        )
