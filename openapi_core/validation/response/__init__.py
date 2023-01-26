"""OpenAPI core validation response module"""
from functools import partial

from openapi_core.unmarshalling.schemas import (
    oas30_response_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.validation.response.proxies import (
    DetectResponseValidatorProxy,
)
from openapi_core.validation.response.proxies import SpecResponseValidatorProxy
from openapi_core.validation.response.validators import (
    APICallResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    APICallResponseHeadersValidator,
)
from openapi_core.validation.response.validators import (
    APICallResponseValidator,
)
from openapi_core.validation.response.validators import (
    V30ResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    V30ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import V30ResponseValidator
from openapi_core.validation.response.validators import (
    V31ResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    V31ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import V31ResponseValidator
from openapi_core.validation.response.validators import (
    V31WebhookResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    V31WebhookResponseHeadersValidator,
)
from openapi_core.validation.response.validators import (
    V31WebhookResponseValidator,
)

__all__ = [
    "V30ResponseDataValidator",
    "V30ResponseHeadersValidator",
    "V30ResponseValidator",
    "V31ResponseDataValidator",
    "V31ResponseHeadersValidator",
    "V31ResponseValidator",
    "V31WebhookResponseDataValidator",
    "V31WebhookResponseHeadersValidator",
    "V31WebhookResponseValidator",
    "V3ResponseValidator",
    "V3WebhookResponseValidator",
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

# alias to the latest v3 version
V3ResponseValidator = V31ResponseValidator
V3WebhookResponseValidator = V31WebhookResponseValidator

# spec validators
openapi_v30_response_data_validator = SpecResponseValidatorProxy(
    APICallResponseDataValidator,
    schema_unmarshallers_factory=oas30_response_schema_unmarshallers_factory,
)
openapi_v30_response_headers_validator = SpecResponseValidatorProxy(
    APICallResponseHeadersValidator,
    schema_unmarshallers_factory=oas30_response_schema_unmarshallers_factory,
)
openapi_v30_response_validator = SpecResponseValidatorProxy(
    APICallResponseValidator,
    schema_unmarshallers_factory=oas30_response_schema_unmarshallers_factory,
    deprecated="openapi_v30_response_validator",
    use="V30ResponseValidator",
)

openapi_v31_response_data_validator = SpecResponseValidatorProxy(
    APICallResponseDataValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_response_headers_validator = SpecResponseValidatorProxy(
    APICallResponseHeadersValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
)
openapi_v31_response_validator = SpecResponseValidatorProxy(
    APICallResponseValidator,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
    deprecated="openapi_v31_response_validator",
    use="V31ResponseValidator",
)

# spec validators alias to the latest v3 version
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
