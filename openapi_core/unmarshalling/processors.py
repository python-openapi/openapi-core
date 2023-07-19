"""OpenAPI core unmarshalling processors module"""
from typing import Any
from typing import Optional
from typing import Type

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.shortcuts import get_classes
from openapi_core.spec import Spec
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class UnmarshallingProcessor:
    def __init__(
        self,
        spec: Spec,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        **unmarshaller_kwargs: Any,
    ):
        self.spec = spec
        if (
            request_unmarshaller_cls is None
            or response_unmarshaller_cls is None
        ):
            classes = get_classes(self.spec)
            if request_unmarshaller_cls is None:
                request_unmarshaller_cls = classes.request_unmarshaller_cls
            if response_unmarshaller_cls is None:
                response_unmarshaller_cls = classes.response_unmarshaller_cls
        self.request_unmarshaller = request_unmarshaller_cls(
            self.spec, **unmarshaller_kwargs
        )
        self.response_unmarshaller = response_unmarshaller_cls(
            self.spec, **unmarshaller_kwargs
        )

    def process_request(self, request: Request) -> RequestUnmarshalResult:
        return self.request_unmarshaller.unmarshal(request)

    def process_response(
        self, request: Request, response: Response
    ) -> ResponseUnmarshalResult:
        return self.response_unmarshaller.unmarshal(request, response)
