from dataclasses import dataclass

from openapi_core.deserializing.exceptions import DeserializeError


@dataclass
class BaseStyleDeserializeError(DeserializeError):
    """Base style deserialize operation error"""

    location: str


@dataclass
class ParameterDeserializeError(BaseStyleDeserializeError):
    """Parameter deserialize operation error"""

    style: str
    value: str

    def __str__(self) -> str:
        return (
            "Failed to deserialize value of "
            f"{self.location} parameter with style {self.style}: {self.value}"
        )


@dataclass(init=False)
class EmptyQueryParameterValue(BaseStyleDeserializeError):
    name: str

    def __init__(self, name: str):
        super().__init__(location="query")
        self.name = name

    def __str__(self) -> str:
        return (
            f"Value of {self.name} {self.location} parameter cannot be empty"
        )
