"""OpenAPI core validation request module"""
from functools import partial

from openapi_core.unmarshalling.schemas import (
    oas30_request_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.validation.request.proxies import (
    DetectSpecRequestValidatorProxy,
)
from openapi_core.validation.request.proxies import SpecRequestValidatorProxy
from openapi_core.validation.request.validators import RequestBodyValidator
from openapi_core.validation.request.validators import (
    RequestParametersValidator,
)
from openapi_core.validation.request.validators import RequestSecurityValidator
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.request.validators import V30RequestBodyValidator
from openapi_core.validation.request.validators import (
    V30RequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V30RequestSecurityValidator,
)
from openapi_core.validation.request.validators import V30RequestValidator
from openapi_core.validation.request.validators import V31RequestBodyValidator
from openapi_core.validation.request.validators import (
    V31RequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V31RequestSecurityValidator,
)
from openapi_core.validation.request.validators import V31RequestValidator
from openapi_core.validation.request.validators import (
    V31WebhookRequestBodyValidator,
)
from openapi_core.validation.request.validators import (
    V31WebhookRequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V31WebhookRequestSecurityValidator,
)
from openapi_core.validation.request.validators import (
    V31WebhookRequestValidator,
)

__all__ = [
    "V30RequestBodyValidator",
    "V30RequestParametersValidator",
    "V30RequestSecurityValidator",
    "V30RequestValidator",
    "V31RequestBodyValidator",
    "V31RequestParametersValidator",
    "V31RequestSecurityValidator",
    "V31RequestValidator",
    "V31WebhookRequestBodyValidator",
    "V31WebhookRequestParametersValidator",
    "V31WebhookRequestSecurityValidator",
    "V31WebhookRequestValidator",
    "V3RequestValidator",
    "V3WebhookRequestValidator",
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

# alias to the latest v3 version
V3RequestValidator = V31RequestValidator
V3WebhookRequestValidator = V31WebhookRequestValidator

# spec validators
openapi_v30_request_body_validator = SpecRequestValidatorProxy(
    RequestBodyValidator,
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)
openapi_v30_request_parameters_validator = SpecRequestValidatorProxy(
    RequestParametersValidator,
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)
openapi_v30_request_security_validator = SpecRequestValidatorProxy(
    RequestSecurityValidator,
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)
openapi_v30_request_validator = SpecRequestValidatorProxy(
    RequestValidator,
    schema_unmarshallers_factory=oas30_request_schema_unmarshallers_factory,
)

openapi_v31_request_body_validator = SpecRequestValidatorProxy(
    RequestBodyValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_request_parameters_validator = SpecRequestValidatorProxy(
    RequestParametersValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_request_security_validator = SpecRequestValidatorProxy(
    RequestSecurityValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_request_validator = SpecRequestValidatorProxy(
    RequestValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)

# spec validators alias to the latest v3 version
openapi_v3_request_body_validator = openapi_v31_request_body_validator
openapi_v3_request_parameters_validator = (
    openapi_v31_request_parameters_validator
)
openapi_v3_request_security_validator = openapi_v31_request_security_validator
openapi_v3_request_validator = openapi_v31_request_validator

# detect version spec
openapi_request_body_validator = DetectSpecRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_body_validator,
        ("openapi", "3.1"): openapi_v31_request_body_validator,
    },
)
openapi_request_parameters_validator = DetectSpecRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_parameters_validator,
        ("openapi", "3.1"): openapi_v31_request_parameters_validator,
    },
)
openapi_request_security_validator = DetectSpecRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_security_validator,
        ("openapi", "3.1"): openapi_v31_request_security_validator,
    },
)
openapi_request_validator = DetectSpecRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_validator,
        ("openapi", "3.1"): openapi_v31_request_validator,
    },
)
