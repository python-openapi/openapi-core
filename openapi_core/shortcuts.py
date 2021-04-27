"""OpenAPI core shortcuts module"""
# backward compatibility
from jsonschema.validators import RefResolver
from openapi_spec_validator import (
    default_handlers, openapi_v3_spec_validator,
)
from openapi_spec_validator.validators import Dereferencer

from openapi_core.spec.paths import SpecPath
from openapi_core.validation.request.shortcuts import (
    spec_validate_body as validate_body,
    spec_validate_parameters as validate_parameters,
)
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.shortcuts import (
    spec_validate_data as validate_data
)
from openapi_core.validation.response.validators import ResponseValidator

__all__ = [
    'create_spec', 'validate_body', 'validate_parameters', 'validate_data',
    'RequestValidator', 'ResponseValidator',
]


def create_spec(
    spec_dict, spec_url='', handlers=default_handlers,
    validate_spec=True,
):
    if validate_spec:
        openapi_v3_spec_validator.validate(spec_dict, spec_url=spec_url)

    spec_resolver = RefResolver(
        spec_url, spec_dict, handlers=handlers)
    dereferencer = Dereferencer(spec_resolver)
    return SpecPath.from_spec(spec_dict, dereferencer)
