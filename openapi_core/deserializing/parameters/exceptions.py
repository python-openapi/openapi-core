from dataclasses import dataclass

from openapi_core.deserializing.exceptions import DeserializeError


@dataclass
class EmptyParameterValue(DeserializeError):
    name: str

    def __str__(self):
        return "Value of parameter cannot be empty: {0}".format(self.name)
