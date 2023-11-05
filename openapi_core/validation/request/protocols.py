"""OpenAPI core validation request protocols module"""
from typing import Iterator
from typing import Optional
from typing import Protocol
from typing import runtime_checkable

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest


@runtime_checkable
class RequestValidator(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def iter_errors(
        self,
        request: Request,
    ) -> Iterator[Exception]:
        ...

    def validate(
        self,
        request: Request,
    ) -> None:
        ...


@runtime_checkable
class WebhookRequestValidator(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def iter_errors(
        self,
        request: WebhookRequest,
    ) -> Iterator[Exception]:
        ...

    def validate(
        self,
        request: WebhookRequest,
    ) -> None:
        ...
