"""OpenAPI core contrib falcon middlewares module"""
from typing import Any, Optional, Type

from falcon import Request, Response

from openapi_core.contrib.falcon.handlers import FalconOpenAPIErrorsHandler
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequestFactory
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponseFactory
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator


class FalconOpenAPIMiddleware:

    request_factory = FalconOpenAPIRequestFactory()
    response_factory = FalconOpenAPIResponseFactory()
    errors_handler = FalconOpenAPIErrorsHandler()

    def __init__(
        self,
        validation_processor: OpenAPIProcessor,
        request_factory: Optional[FalconOpenAPIRequestFactory] = None,
        response_factory: Optional[FalconOpenAPIResponseFactory] = None,
        errors_handler: Optional[FalconOpenAPIErrorsHandler] = None,
    ):
        self.validation_processor = validation_processor
        self.request_factory = request_factory or self.request_factory
        self.response_factory = response_factory or self.response_factory
        self.errors_handler = errors_handler or self.errors_handler

    @classmethod
    def from_spec(
        cls,
        spec: SpecPath,
        request_factory: Optional[FalconOpenAPIRequestFactory] = None,
        response_factory: Optional[FalconOpenAPIResponseFactory] = None,
        errors_handler: Optional[FalconOpenAPIErrorsHandler] = None,
    ):
        request_validator = RequestValidator(spec)
        response_validator = ResponseValidator(spec)
        validation_processor = OpenAPIProcessor(
            request_validator, response_validator)
        return cls(
            validation_processor,
            request_factory=request_factory,
            response_factory=response_factory,
            errors_handler=errors_handler,
        )

    def process_request(self, req: Request, resp: Response):
        openapi_req = self._get_openapi_request(req)
        req.context.openapi = self._process_openapi_request(openapi_req)
        if req.context.openapi.errors:
            return self._handle_request_errors(req, resp, req.context.openapi)

    def process_response(
        self,
        req: Request,
        resp: Response,
        resource: Optional[Any],
        req_succeeded: bool,
    ):
        openapi_req = self._get_openapi_request(req)
        openapi_resp = self._get_openapi_response(resp)
        resp.context.openapi = self._process_openapi_response(
            openapi_req, openapi_resp)
        if resp.context.openapi.errors:
            return self._handle_response_errors(
                req, resp, resp.context.openapi)

    def _handle_request_errors(
        self,
        req: Request,
        resp: Response,
        request_result,
    ):
        return self.errors_handler.handle(req, resp, request_result.errors)

    def _handle_response_errors(
        self,
        req: Request,
        resp: Response,
        response_result,
    ):
        return self.errors_handler.handle(req, resp, response_result.errors)

    def _get_openapi_request(self, request: Request) -> OpenAPIRequest:
        return self.request_factory.create(request)

    def _get_openapi_response(self, response: Response) -> OpenAPIResponse:
        return self.response_factory.create(response)

    def _process_openapi_request(self, openapi_request: OpenAPIRequest):
        return self.validation_processor.process_request(openapi_request)

    def _process_openapi_response(
        self,
        opneapi_request: OpenAPIRequest,
        openapi_response: OpenAPIProcessor,
    ):
        return self.validation_processor.process_response(
            opneapi_request, openapi_response)
