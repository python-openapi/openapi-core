from aioitertools.itertools import tee as atee
from starlette.requests import Request
from starlette.responses import Response

from openapi_core.contrib.starlette.requests import StarletteOpenAPIRequest
from openapi_core.contrib.starlette.responses import StarletteOpenAPIResponse
from openapi_core.unmarshalling.processors import AsyncUnmarshallingProcessor
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable


class StarletteIntegration(AsyncUnmarshallingProcessor[Request, Response]):
    request_cls = StarletteOpenAPIRequest
    response_cls = StarletteOpenAPIResponse

    async def get_openapi_request(
        self, request: Request
    ) -> StarletteOpenAPIRequest:
        body = await request.body()
        return self.request_cls(request, body)

    async def get_openapi_response(
        self, response: Response
    ) -> StarletteOpenAPIResponse:
        assert self.response_cls is not None
        data = None
        if hasattr(response, "body_iterator"):
            body_iter1, body_iter2 = atee(response.body_iterator)
            response.body_iterator = body_iter2
            data = b"".join(
                [
                    (
                        chunk.encode(response.charset)
                        if not isinstance(chunk, bytes)
                        else chunk
                    )
                    async for chunk in body_iter1
                ]
            )
        return self.response_cls(response, data=data)

    def should_validate_response(self) -> bool:
        return self.response_cls is not None

    async def handle_response(
        self,
        request: Request,
        response: Response,
        errors_handler: ErrorsHandlerCallable[Response],
    ) -> Response:
        if not self.should_validate_response():
            return response
        return await super().handle_response(request, response, errors_handler)
