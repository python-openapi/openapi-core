"""OpenAPI core shortcuts module"""
# backward compatibility
from openapi_core.spec.shortcuts import create_spec
from openapi_core.validation.request.shortcuts import (
    validate_request,
    spec_validate_body, spec_validate_parameters, spec_validate_security,
)
from openapi_core.validation.response.shortcuts import (
    validate_response,
    spec_validate_data, spec_validate_headers,
)

__all__ = [
    'create_spec',
    'validate_request', 'validate_response',
    'spec_validate_body', 'spec_validate_parameters', 'spec_validate_security',
    'spec_validate_data', 'spec_validate_headers',
]
