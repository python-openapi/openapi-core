"""OpenAPI core validation types module"""
from typing import Union

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.exceptions import MissingRequiredParameter
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.responses.exceptions import ResponseFinderError
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.validation.exceptions import InvalidSecurity


ProcessErrors = Union[
    DeserializeError, CastError, ValidateError, UnmarshalError,
]


# equivalent to
# ProcessErrors | MissingRequiredParameter
ParameterErrors = Union[
    DeserializeError, CastError, ValidateError, UnmarshalError,
    MissingRequiredParameter,
]


# equivalent to
# ParameterErrors | PathError | ResponseFinderError | InvalidSecurity
ValidationErrors = Union[
    DeserializeError, CastError, ValidateError, UnmarshalError,
    MissingRequiredParameter,
    PathError, ResponseFinderError, InvalidSecurity,
]
