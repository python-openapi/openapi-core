"""OpenAPI core shortcuts module"""
# backward compatibility
from openapi_core.validation.request.shortcuts import spec_validate_body
from openapi_core.validation.request.shortcuts import spec_validate_parameters
from openapi_core.validation.request.shortcuts import spec_validate_security
from openapi_core.validation.request.shortcuts import validate_request
from openapi_core.validation.response.shortcuts import spec_validate_data
from openapi_core.validation.response.shortcuts import spec_validate_headers
from openapi_core.validation.response.shortcuts import validate_response

__all__ = [
    "validate_request",
    "validate_response",
    "spec_validate_body",
    "spec_validate_parameters",
    "spec_validate_security",
    "spec_validate_data",
    "spec_validate_headers",
]
