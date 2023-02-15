from typing import Type
from typing import Union

from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.protocols import WebhookRequestValidator

RequestValidatorType = Type[RequestValidator]
WebhookRequestValidatorType = Type[WebhookRequestValidator]
AnyRequestValidatorType = Union[
    RequestValidatorType, WebhookRequestValidatorType
]
