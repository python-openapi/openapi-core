"""OpenAPI core validation request protocols module"""
from typing import Optional
from typing import Protocol
from typing import runtime_checkable

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


@runtime_checkable
class RequestUnmarshaller(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def unmarshal(
        self,
        request: Request,
    ) -> RequestUnmarshalResult:
        ...


@runtime_checkable
class WebhookRequestUnmarshaller(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def unmarshal(
        self,
        request: WebhookRequest,
    ) -> RequestUnmarshalResult:
        ...
