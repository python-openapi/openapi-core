from typing import Type
from typing import Union

from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.protocols import WebhookResponseValidator

ResponseValidatorType = Type[ResponseValidator]
WebhookResponseValidatorType = Type[WebhookResponseValidator]
AnyResponseValidatorType = Union[
    ResponseValidatorType, WebhookResponseValidatorType
]
