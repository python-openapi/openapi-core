"""OpenAPI core validation response types module"""
from typing import Union

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.exceptions import MissingRequiredHeader
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.validation.response.exceptions import MissingResponseContent


# equivalent to
# ProcessErrors | MediaTypeFinderError | MissingResponseContent
DataErrors = Union[
    DeserializeError, CastError, ValidateError, UnmarshalError,
    MediaTypeFinderError, MissingResponseContent,
]


# equivalent to
# ProcessErrors | MissingRequiredHeader
HeadersErrors = Union[
    DeserializeError, CastError, ValidateError, UnmarshalError,
    MissingRequiredHeader,
]
