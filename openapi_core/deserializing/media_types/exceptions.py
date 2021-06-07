from dataclasses import dataclass

from openapi_core.deserializing.exceptions import DeserializeError


@dataclass
class MediaTypeDeserializeError(DeserializeError):
    """Media type deserialize operation error"""
    mimetype: str
    value: str

    def __str__(self):
        return (
            "Failed to deserialize value with {mimetype} mimetype: {value}"
        ).format(value=self.value, mimetype=self.mimetype)
