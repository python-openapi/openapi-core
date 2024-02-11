"""OpenAPI core validation response module"""

from typing import Mapping

from openapi_spec_validator.versions import consts as versions
from openapi_spec_validator.versions.datatypes import SpecVersion

from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType
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
    "VALIDATORS",
    "WEBHOOK_VALIDATORS",
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
]

# versions mapping
VALIDATORS: Mapping[SpecVersion, ResponseValidatorType] = {
    versions.OPENAPIV30: V30ResponseValidator,
    versions.OPENAPIV31: V31ResponseValidator,
}
WEBHOOK_VALIDATORS: Mapping[SpecVersion, WebhookResponseValidatorType] = {
    versions.OPENAPIV31: V31WebhookResponseValidator,
}

# alias to the latest v3 version
V3ResponseValidator = V31ResponseValidator
V3WebhookResponseValidator = V31WebhookResponseValidator
