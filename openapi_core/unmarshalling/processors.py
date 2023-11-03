"""OpenAPI core unmarshalling processors module"""
from typing import Any
from typing import Generic
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.shortcuts import get_classes
from openapi_core.typing import AsyncValidRequestHandlerCallable
from openapi_core.typing import ErrorsHandlerCallable
from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType
from openapi_core.typing import ValidRequestHandlerCallable
from openapi_core.unmarshalling.request.processors import (
    RequestUnmarshallingProcessor,
)
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.processors import (
    ResponseUnmarshallingProcessor,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class UnmarshallingProcessor(Generic[RequestType, ResponseType]):
    def __init__(
        self,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        **unmarshaller_kwargs: Any,
    ):
        if (
            request_unmarshaller_cls is None
            or response_unmarshaller_cls is None
        ):
            classes = get_classes(spec)
            if request_unmarshaller_cls is None:
                request_unmarshaller_cls = classes.request_unmarshaller_cls
            if response_unmarshaller_cls is None:
                response_unmarshaller_cls = classes.response_unmarshaller_cls

        self.request_processor = RequestUnmarshallingProcessor(
            spec,
            request_unmarshaller_cls,
            **unmarshaller_kwargs,
        )
        self.response_processor = ResponseUnmarshallingProcessor(
            spec,
            response_unmarshaller_cls,
            **unmarshaller_kwargs,
        )

    def _get_openapi_request(self, request: RequestType) -> Request:
        raise NotImplementedError

    def _get_openapi_response(self, response: ResponseType) -> Response:
        raise NotImplementedError

    def _validate_response(self) -> bool:
        raise NotImplementedError

    def handle_request(
        self,
        request: RequestType,
        valid_handler: ValidRequestHandlerCallable[ResponseType],
        errors_handler: ErrorsHandlerCallable[ResponseType],
    ) -> ResponseType:
        openapi_request = self._get_openapi_request(request)
        request_unmarshal_result = self.request_processor.process(
            openapi_request
        )
        if request_unmarshal_result.errors:
            return errors_handler(request_unmarshal_result.errors)
        return valid_handler(request_unmarshal_result)

    def handle_response(
        self,
        request: RequestType,
        response: ResponseType,
        errors_handler: ErrorsHandlerCallable[ResponseType],
    ) -> ResponseType:
        if not self._validate_response():
            return response
        openapi_request = self._get_openapi_request(request)
        openapi_response = self._get_openapi_response(response)
        response_unmarshal_result = self.response_processor.process(
            openapi_request, openapi_response
        )
        if response_unmarshal_result.errors:
            return errors_handler(response_unmarshal_result.errors)
        return response


class AsyncUnmarshallingProcessor(Generic[RequestType, ResponseType]):
    def __init__(
        self,
        spec: SchemaPath,
        request_unmarshaller_cls: Optional[RequestUnmarshallerType] = None,
        response_unmarshaller_cls: Optional[ResponseUnmarshallerType] = None,
        **unmarshaller_kwargs: Any,
    ):
        if (
            request_unmarshaller_cls is None
            or response_unmarshaller_cls is None
        ):
            classes = get_classes(spec)
            if request_unmarshaller_cls is None:
                request_unmarshaller_cls = classes.request_unmarshaller_cls
            if response_unmarshaller_cls is None:
                response_unmarshaller_cls = classes.response_unmarshaller_cls

        self.request_processor = RequestUnmarshallingProcessor(
            spec,
            request_unmarshaller_cls,
            **unmarshaller_kwargs,
        )
        self.response_processor = ResponseUnmarshallingProcessor(
            spec,
            response_unmarshaller_cls,
            **unmarshaller_kwargs,
        )

    async def _get_openapi_request(self, request: RequestType) -> Request:
        raise NotImplementedError

    async def _get_openapi_response(self, response: ResponseType) -> Response:
        raise NotImplementedError

    def _validate_response(self) -> bool:
        raise NotImplementedError

    async def handle_request(
        self,
        request: RequestType,
        valid_handler: AsyncValidRequestHandlerCallable[ResponseType],
        errors_handler: ErrorsHandlerCallable[ResponseType],
    ) -> ResponseType:
        openapi_request = await self._get_openapi_request(request)
        request_unmarshal_result = self.request_processor.process(
            openapi_request
        )
        if request_unmarshal_result.errors:
            return errors_handler(request_unmarshal_result.errors)
        result = await valid_handler(request_unmarshal_result)
        return result

    async def handle_response(
        self,
        request: RequestType,
        response: ResponseType,
        errors_handler: ErrorsHandlerCallable[ResponseType],
    ) -> ResponseType:
        if not self._validate_response():
            return response
        openapi_request = await self._get_openapi_request(request)
        openapi_response = await self._get_openapi_response(response)
        response_unmarshal_result = self.response_processor.process(
            openapi_request, openapi_response
        )
        if response_unmarshal_result.errors:
            return errors_handler(response_unmarshal_result.errors)
        return response
