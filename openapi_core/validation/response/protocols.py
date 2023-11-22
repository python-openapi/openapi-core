"""OpenAPI core validation response protocols module"""
from typing import Iterator
from typing import Optional
from typing import Protocol
from typing import runtime_checkable

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest


@runtime_checkable
class ResponseValidator(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        ...

    def validate(
        self,
        request: Request,
        response: Response,
    ) -> None:
        ...


@runtime_checkable
class WebhookResponseValidator(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        ...

    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> None:
        ...
