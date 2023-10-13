"""OpenAPI core validation response protocols module"""
from typing import Any
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import runtime_checkable

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)


@runtime_checkable
class ResponseUnmarshaller(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def unmarshal(
        self,
        request: Request,
        response: Response,
    ) -> ResponseUnmarshalResult:
        ...


@runtime_checkable
class WebhookResponseUnmarshaller(Protocol):
    def __init__(self, spec: SchemaPath, base_url: Optional[str] = None):
        ...

    def unmarshal(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseUnmarshalResult:
        ...
