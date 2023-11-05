from falcon.request import Request
from falcon.response import Response

from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable


class FalconIntegration(UnmarshallingProcessor[Request, Response]):
    request_cls = FalconOpenAPIRequest
    response_cls = FalconOpenAPIResponse

    def get_openapi_request(self, request: Request) -> FalconOpenAPIRequest:
        return self.request_cls(request)

    def get_openapi_response(
        self, response: Response
    ) -> FalconOpenAPIResponse:
        assert self.response_cls is not None
        return self.response_cls(response)

    def should_validate_response(self) -> bool:
        return self.response_cls is not None

    def handle_response(
        self,
        request: Request,
        response: Response,
        errors_handler: ErrorsHandlerCallable[Response],
    ) -> Response:
        if not self.should_validate_response():
            return response
        return super().handle_response(request, response, errors_handler)
