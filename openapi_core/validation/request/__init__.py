"""OpenAPI core validation request module"""
from openapi_core.unmarshalling.schemas import (
    oas30_request_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.validation.request.proxies import DetectRequestValidatorProxy
from openapi_core.validation.request.validators import RequestBodyValidator
from openapi_core.validation.request.validators import (
    RequestParametersValidator,
)
from openapi_core.validation.request.validators import RequestSecurityValidator
from openapi_core.validation.request.validators import RequestValidator

__all__ = [
    "openapi_v30_request_body_validator",
    "openapi_v30_request_parameters_validator",
    "openapi_v30_request_security_validator",
    "openapi_v30_request_validator",
    "openapi_v31_request_body_validator",
    "openapi_v31_request_parameters_validator",
    "openapi_v31_request_security_validator",
    "openapi_v31_request_validator",
    "openapi_v3_request_body_validator",
    "openapi_v3_request_parameters_validator",
    "openapi_v3_request_security_validator",
    "openapi_v3_request_validator",
    "openapi_request_body_validator",
    "openapi_request_parameters_validator",
    "openapi_request_security_validator",
    "openapi_request_validator",
]

openapi_v30_request_body_validator = RequestBodyValidator(
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)
openapi_v30_request_parameters_validator = RequestParametersValidator(
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)
openapi_v30_request_security_validator = RequestSecurityValidator(
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)
openapi_v30_request_validator = RequestValidator(
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)

openapi_v31_request_body_validator = RequestBodyValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_request_parameters_validator = RequestParametersValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_request_security_validator = RequestSecurityValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_request_validator = RequestValidator(
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)

# alias to the latest v3 version
openapi_v3_request_body_validator = openapi_v31_request_body_validator
openapi_v3_request_parameters_validator = (
    openapi_v31_request_parameters_validator
)
openapi_v3_request_security_validator = openapi_v31_request_security_validator
openapi_v3_request_validator = openapi_v31_request_validator

# detect version spec
openapi_request_body_validator = DetectRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_body_validator,
        ("openapi", "3.1"): openapi_v31_request_body_validator,
    },
)
openapi_request_parameters_validator = DetectRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_parameters_validator,
        ("openapi", "3.1"): openapi_v31_request_parameters_validator,
    },
)
openapi_request_security_validator = DetectRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_security_validator,
        ("openapi", "3.1"): openapi_v31_request_security_validator,
    },
)
openapi_request_validator = DetectRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_validator,
        ("openapi", "3.1"): openapi_v31_request_validator,
    },
)
