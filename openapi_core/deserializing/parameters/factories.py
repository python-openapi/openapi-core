from functools import partial

from openapi_core.deserializing.parameters.deserializers import (
    CallableParameterDeserializer, UnsupportedStyleDeserializer,
)
from openapi_core.deserializing.parameters.util import split
from openapi_core.schema.parameters import get_style


class ParameterDeserializersFactory:

    PARAMETER_STYLE_DESERIALIZERS = {
        'form': partial(split, separator=','),
        'simple': partial(split, separator=','),
        'spaceDelimited': partial(split, separator=' '),
        'pipeDelimited': partial(split, separator='|'),
    }

    def create(self, param_or_header):
        style = get_style(param_or_header)

        if style not in self.PARAMETER_STYLE_DESERIALIZERS:
            return UnsupportedStyleDeserializer(param_or_header, style)

        deserialize_callable = self.PARAMETER_STYLE_DESERIALIZERS[style]
        return CallableParameterDeserializer(
            param_or_header, style, deserialize_callable)
