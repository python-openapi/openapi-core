from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.parameters.exceptions import (
    EmptyParameterValue,
)
from openapi_core.schema.parameters.enums import ParameterLocation


class PrimitiveDeserializer(object):

    def __init__(self, param, deserializer_callable):
        self.param = param
        self.deserializer_callable = deserializer_callable

    def __call__(self, value):
        if (self.param.location == ParameterLocation.QUERY and value == "" and
                not self.param.allow_empty_value):
            raise EmptyParameterValue(
                value, self.param.style, self.param.name)

        if not self.param.aslist or self.param.explode:
            return value
        try:
            return self.deserializer_callable(value)
        except (ValueError, TypeError, AttributeError):
            raise DeserializeError(value, self.param.style)
