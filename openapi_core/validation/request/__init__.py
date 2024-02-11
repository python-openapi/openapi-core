"""OpenAPI core validation request module"""

from typing import Mapping

from openapi_spec_validator.versions import consts as versions
from openapi_spec_validator.versions.datatypes import SpecVersion

from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
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
    "VALIDATORS",
    "WEBHOOK_VALIDATORS",
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
]

# versions mapping
VALIDATORS: Mapping[SpecVersion, RequestValidatorType] = {
    versions.OPENAPIV30: V30RequestValidator,
    versions.OPENAPIV31: V31RequestValidator,
}
WEBHOOK_VALIDATORS: Mapping[SpecVersion, WebhookRequestValidatorType] = {
    versions.OPENAPIV31: V31WebhookRequestValidator,
}

# alias to the latest v3 version
V3RequestValidator = V31RequestValidator
V3WebhookRequestValidator = V31WebhookRequestValidator
