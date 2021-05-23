"""OpenAPI core validation request types module"""
from typing import Union

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
)

# equivalent to
# ProcessErrors | MissingRequiredRequestBody | MediaTypeFinderError
BodyErrors = Union[
    DeserializeError, CastError, ValidateError, UnmarshalError,
    MissingRequiredRequestBody, MediaTypeFinderError,
]
