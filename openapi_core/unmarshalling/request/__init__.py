"""OpenAPI core unmarshalling request module"""
from openapi_core.unmarshalling.request.proxies import (
    DetectSpecRequestValidatorProxy,
)
from openapi_core.unmarshalling.request.proxies import (
    SpecRequestValidatorProxy,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    APICallRequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import RequestValidator
from openapi_core.unmarshalling.request.unmarshallers import (
    V30RequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V31RequestUnmarshaller,
)
from openapi_core.unmarshalling.request.unmarshallers import (
    V31WebhookRequestUnmarshaller,
)
from openapi_core.unmarshalling.schemas import (
    oas30_write_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)

__all__ = [
    "V30RequestUnmarshaller",
    "V31RequestUnmarshaller",
    "V31WebhookRequestUnmarshaller",
    "RequestValidator",
    "openapi_v30_request_validator",
    "openapi_v31_request_validator",
    "openapi_v3_request_validator",
    "openapi_request_validator",
]

# alias to the latest v3 version
V3RequestUnmarshaller = V31RequestUnmarshaller
V3WebhookRequestUnmarshaller = V31WebhookRequestUnmarshaller

# spec validators
openapi_v30_request_validator = SpecRequestValidatorProxy(
    APICallRequestUnmarshaller,
    schema_unmarshallers_factory=oas30_write_schema_unmarshallers_factory,
    deprecated="openapi_v30_request_validator",
    use="V30RequestValidator",
)
openapi_v31_request_validator = SpecRequestValidatorProxy(
    APICallRequestUnmarshaller,
    schema_unmarshallers_factory=oas31_schema_unmarshallers_factory,
    deprecated="openapi_v31_request_validator",
    use="V31RequestValidator",
)

# spec validators alias to the latest v3 version
openapi_v3_request_validator = openapi_v31_request_validator

# detect version spec
openapi_request_validator = DetectSpecRequestValidatorProxy(
    {
        ("openapi", "3.0"): openapi_v30_request_validator,
        ("openapi", "3.1"): openapi_v31_request_validator,
    },
)
