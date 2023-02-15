"""OpenAPI core unmarshalling response module"""
from openapi_core.unmarshalling.response.proxies import (
    DetectResponseValidatorProxy,
)
from openapi_core.unmarshalling.response.proxies import (
    SpecResponseValidatorProxy,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    APICallResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import ResponseValidator
from openapi_core.unmarshalling.response.unmarshallers import (
    V30ResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V31ResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.unmarshallers import (
    V31WebhookResponseUnmarshaller,
)
from openapi_core.unmarshalling.schemas import (
    oas30_read_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)

__all__ = [
    "V30ResponseUnmarshaller",
    "V31ResponseUnmarshaller",
    "V31WebhookResponseUnmarshaller",
    "ResponseValidator",
    "openapi_v30_response_validator",
    "openapi_v31_response_validator",
    "openapi_v3_response_validator",
    "openapi_response_validator",
]

# alias to the latest v3 version
V3ResponseUnmarshaller = V31ResponseUnmarshaller
V3WebhookResponseUnmarshaller = V31WebhookResponseUnmarshaller

# spec validators
openapi_v30_response_validator = SpecResponseValidatorProxy(
    APICallResponseUnmarshaller,
    schema_unmarshallers_factory=oas30_read_schema_unmarshallers_factory,
    deprecated="openapi_v30_response_validator",
    use="V30ResponseUnmarshaller",
)

openapi_v31_response_validator = SpecResponseValidatorProxy(
    APICallResponseUnmarshaller,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
    deprecated="openapi_v31_response_validator",
    use="V31ResponseUnmarshaller",
)

# spec validators alias to the latest v3 version
openapi_v3_response_validator = openapi_v31_response_validator

# detect version spec
openapi_response_validator = DetectResponseValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_response_validator,
        ("openapi", "3.1"): openapi_v31_response_validator,
    },
)
