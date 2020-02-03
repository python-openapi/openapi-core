import warnings

from openapi_core.deserializing.parameters.deserializers import (
    PrimitiveDeserializer,
)
from openapi_core.schema.parameters.enums import ParameterStyle


class ParameterDeserializersFactory(object):

    PARAMETER_STYLE_DESERIALIZERS = {
        ParameterStyle.FORM: lambda x: x.split(','),
        ParameterStyle.SIMPLE: lambda x: x.split(','),
        ParameterStyle.SPACE_DELIMITED: lambda x: x.split(' '),
        ParameterStyle.PIPE_DELIMITED: lambda x: x.split('|'),
    }

    def create(self, param):
        if param.deprecated:
            warnings.warn(
                "{0} parameter is deprecated".format(param.name),
                DeprecationWarning,
            )

        deserialize_callable = self.PARAMETER_STYLE_DESERIALIZERS[param.style]
        return PrimitiveDeserializer(param, deserialize_callable)
