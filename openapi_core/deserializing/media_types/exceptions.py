from dataclasses import dataclass

from openapi_core.deserializing.exceptions import DeserializeError


@dataclass
class MediaTypeDeserializeError(DeserializeError):
    """Media type deserialize operation error"""

    mimetype: str
    value: bytes

    def __str__(self) -> str:
        return (
            "Failed to deserialize value with {mimetype} mimetype: {value}"
        ).format(value=self.value.decode("utf-8"), mimetype=self.mimetype)
