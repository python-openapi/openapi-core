"""OpenAPI core unmarshalling processors module"""
from typing import Any
from typing import Generic
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.typing import RequestType
from openapi_core.typing import ResponseType
from openapi_core.unmarshalling.integrations import (
    AsyncUnmarshallingIntegration,
)
from openapi_core.unmarshalling.integrations import UnmarshallingIntegration
from openapi_core.unmarshalling.request.processors import (
    RequestUnmarshallingProcessor,
)
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.processors import (
    ResponseUnmarshallingProcessor,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.typing import AsyncValidRequestHandlerCallable
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable
from openapi_core.unmarshalling.typing import ValidRequestHandlerCallable


class UnmarshallingProcessor(
    UnmarshallingIntegration[RequestType, ResponseType]
):
    def handle_request(
        self,
        request: RequestType,
        valid_handler: ValidRequestHandlerCallable[ResponseType],
        errors_handler: ErrorsHandlerCallable[ResponseType],
    ) -> ResponseType:
        request_unmarshal_result = self.unmarshal_request(
            request,
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
        response_unmarshal_result = self.unmarshal_response(request, response)
        if response_unmarshal_result.errors:
            return errors_handler(response_unmarshal_result.errors)
        return response


class AsyncUnmarshallingProcessor(
    AsyncUnmarshallingIntegration[RequestType, ResponseType]
):
    async def handle_request(
        self,
        request: RequestType,
        valid_handler: AsyncValidRequestHandlerCallable[ResponseType],
        errors_handler: ErrorsHandlerCallable[ResponseType],
    ) -> ResponseType:
        request_unmarshal_result = await self.unmarshal_request(request)
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
        response_unmarshal_result = await self.unmarshal_response(
            request, response
        )
        if response_unmarshal_result.errors:
            return errors_handler(response_unmarshal_result.errors)
        return response
