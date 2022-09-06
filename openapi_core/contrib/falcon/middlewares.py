"""OpenAPI core contrib falcon middlewares module"""

from openapi_core.contrib.falcon.handlers import FalconOpenAPIErrorsHandler
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator


class FalconOpenAPIMiddleware:

    request_class = FalconOpenAPIRequest
    response_class = FalconOpenAPIResponse
    errors_handler = FalconOpenAPIErrorsHandler()

    def __init__(
        self,
        spec,
        validation_processor,
        request_class=None,
        response_class=None,
        errors_handler=None,
    ):
        self.spec = spec
        self.validation_processor = validation_processor
        self.request_class = request_class or self.request_class
        self.response_class = response_class or self.response_class
        self.errors_handler = errors_handler or self.errors_handler

    @classmethod
    def from_spec(
        cls,
        spec,
        request_class=None,
        response_class=None,
        errors_handler=None,
    ):
        validation_processor = OpenAPIProcessor(
            openapi_request_validator, openapi_response_validator
        )
        return cls(
            spec,
            validation_processor,
            request_class=request_class,
            response_class=response_class,
            errors_handler=errors_handler,
        )

    def process_request(self, req, resp):
        openapi_req = self._get_openapi_request(req)
        req.context.openapi = self._process_openapi_request(openapi_req)
        if req.context.openapi.errors:
            return self._handle_request_errors(req, resp, req.context.openapi)

    def process_response(self, req, resp, resource, req_succeeded):
        openapi_req = self._get_openapi_request(req)
        openapi_resp = self._get_openapi_response(resp)
        resp.context.openapi = self._process_openapi_response(
            openapi_req, openapi_resp
        )
        if resp.context.openapi.errors:
            return self._handle_response_errors(
                req, resp, resp.context.openapi
            )

    def _handle_request_errors(self, req, resp, request_result):
        return self.errors_handler.handle(req, resp, request_result.errors)

    def _handle_response_errors(self, req, resp, response_result):
        return self.errors_handler.handle(req, resp, response_result.errors)

    def _get_openapi_request(self, request):
        return self.request_class(request)

    def _get_openapi_response(self, response):
        return self.response_class(response)

    def _process_openapi_request(self, openapi_request):
        return self.validation_processor.process_request(
            self.spec, openapi_request
        )

    def _process_openapi_response(self, opneapi_request, openapi_response):
        return self.validation_processor.process_response(
            self.spec, opneapi_request, openapi_response
        )
