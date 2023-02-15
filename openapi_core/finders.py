from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Type

from openapi_core.exceptions import SpecError
from openapi_core.spec import Spec
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType
from openapi_core.validation.validators import BaseValidator


class SpecVersion(NamedTuple):
    name: str
    version: str


class SpecClasses(NamedTuple):
    request_validator_cls: RequestValidatorType
    response_validator_cls: ResponseValidatorType
    webhook_request_validator_cls: Optional[WebhookRequestValidatorType]
    webhook_response_validator_cls: Optional[WebhookResponseValidatorType]
    request_unmarshaller_cls: RequestUnmarshallerType
    response_unmarshaller_cls: ResponseUnmarshallerType
    webhook_request_unmarshaller_cls: Optional[WebhookRequestUnmarshallerType]
    webhook_response_unmarshaller_cls: Optional[
        WebhookResponseUnmarshallerType
    ]


class SpecFinder:
    def __init__(self, specs: Mapping[SpecVersion, SpecClasses]) -> None:
        self.specs = specs

    def get_classes(self, spec: Spec) -> SpecClasses:
        for v, classes in self.specs.items():
            if v.name in spec and spec[v.name].startswith(v.version):
                return classes
        raise SpecError("Spec schema version not detected")
