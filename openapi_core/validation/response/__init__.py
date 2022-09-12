"""OpenAPI core validation response module"""
from openapi_core.unmarshalling.schemas import (
    oas30_response_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.validation.response.proxies import (
    DetectResponseValidatorProxy,
)
from openapi_core.validation.response.validators import ResponseDataValidator
from openapi_core.validation.response.validators import (
    ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import ResponseValidator

__all__ = [
    "openapi_v30_response_data_validator",
    "openapi_v30_response_headers_validator",
    "openapi_v30_response_validator",
    "openapi_v31_response_data_validator",
    "openapi_v31_response_headers_validator",
    "openapi_v31_response_validator",
    "openapi_v3_response_data_validator",
    "openapi_v3_response_headers_validator",
    "openapi_v3_response_validator",
    "openapi_response_data_validator",
    "openapi_response_headers_validator",
    "openapi_response_validator",
]

openapi_v30_response_data_validator = ResponseDataValidator(
    schema_unmarshallers_factory=oas30_response_schema_unmarshallers_factory,
)
openapi_v30_response_headers_validator = ResponseHeadersValidator(
    schema_unmarshallers_factory=oas30_response_schema_unmarshallers_factory,
)
openapi_v30_response_validator = ResponseValidator(
    schema_unmarshallers_factory=oas30_response_schema_unmarshallers_factory,
)

openapi_v31_response_data_validator = ResponseDataValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_response_headers_validator = ResponseHeadersValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_response_validator = ResponseValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)

# alias to the latest v3 version
openapi_v3_response_data_validator = openapi_v31_response_data_validator
openapi_v3_response_headers_validator = openapi_v31_response_headers_validator
openapi_v3_response_validator = openapi_v31_response_validator

# detect version spec
openapi_response_data_validator = DetectResponseValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_response_data_validator,
        ("openapi", "3.1"): openapi_v31_response_data_validator,
    },
)
openapi_response_headers_validator = DetectResponseValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_response_headers_validator,
        ("openapi", "3.1"): openapi_v31_response_headers_validator,
    },
)
openapi_response_validator = DetectResponseValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_response_validator,
        ("openapi", "3.1"): openapi_v31_response_validator,
    },
)
