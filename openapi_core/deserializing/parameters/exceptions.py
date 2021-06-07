from dataclasses import dataclass

from openapi_core.deserializing.exceptions import DeserializeError


@dataclass
class BaseParameterDeserializeError(DeserializeError):
    """Base parameter deserialize operation error"""
    location: str


@dataclass
class ParameterDeserializeError(BaseParameterDeserializeError):
    """Parameter deserialize operation error"""
    style: str
    value: str

    def __str__(self):
        return (
            "Failed to deserialize value "
            "of {location} parameter with style {style}: {value}"
        ).format(location=self.location, style=self.style, value=self.value)


@dataclass(init=False)
class EmptyQueryParameterValue(BaseParameterDeserializeError):
    name: str

    def __init__(self, name):
        super().__init__(location='query')
        self.name = name

    def __str__(self):
        return "Value of {name} {location} parameter cannot be empty".format(
            name=self.name, location=self.location)
