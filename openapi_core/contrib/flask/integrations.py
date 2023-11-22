from flask.wrappers import Request
from flask.wrappers import Response

from openapi_core.contrib.flask.requests import FlaskOpenAPIRequest
from openapi_core.contrib.flask.responses import FlaskOpenAPIResponse
from openapi_core.unmarshalling.processors import UnmarshallingProcessor
from openapi_core.unmarshalling.typing import ErrorsHandlerCallable


class FlaskIntegration(UnmarshallingProcessor[Request, Response]):
    request_cls = FlaskOpenAPIRequest
    response_cls = FlaskOpenAPIResponse

    def get_openapi_request(self, request: Request) -> FlaskOpenAPIRequest:
        return self.request_cls(request)

    def get_openapi_response(self, response: Response) -> FlaskOpenAPIResponse:
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
