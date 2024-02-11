"""OpenAPI core contrib falcon middlewares module"""

from typing import Any
from typing import Type
from typing import Union

from falcon.request import Request
from falcon.response import Response
from jsonschema._utils import Unset
from jsonschema.validators import _UNSET
from jsonschema_path import SchemaPath

from openapi_core import Config
from openapi_core import OpenAPI
from openapi_core.contrib.falcon.handlers import FalconOpenAPIErrorsHandler
from openapi_core.contrib.falcon.handlers import (
    FalconOpenAPIValidRequestHandler,
)
from openapi_core.contrib.falcon.integrations import FalconIntegration
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class FalconOpenAPIMiddleware(FalconIntegration):
    valid_request_handler_cls = FalconOpenAPIValidRequestHandler
    errors_handler_cls: Type[FalconOpenAPIErrorsHandler] = (
        FalconOpenAPIErrorsHandler
    )

    def __init__(
        self,
        openapi: OpenAPI,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ):
        super().__init__(openapi)
        self.request_cls = request_cls or self.request_cls
        self.response_cls = response_cls or self.response_cls
        self.errors_handler_cls = errors_handler_cls or self.errors_handler_cls

    @classmethod
    def from_spec(
        cls,
        spec: SchemaPath,
        request_unmarshaller_cls: Union[
            RequestUnmarshallerType, Unset
        ] = _UNSET,
        response_unmarshaller_cls: Union[
            ResponseUnmarshallerType, Unset
        ] = _UNSET,
        request_cls: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_cls: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler_cls: Type[
            FalconOpenAPIErrorsHandler
        ] = FalconOpenAPIErrorsHandler,
        **unmarshaller_kwargs: Any,
    ) -> "FalconOpenAPIMiddleware":
        config = Config(
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
        )
        openapi = OpenAPI(spec, config=config)
        return cls(
            openapi,
            request_unmarshaller_cls=request_unmarshaller_cls,
            response_unmarshaller_cls=response_unmarshaller_cls,
            request_cls=request_cls,
            response_cls=response_cls,
            errors_handler_cls=errors_handler_cls,
            **unmarshaller_kwargs,
        )

    def process_request(self, req: Request, resp: Response) -> None:
        valid_handler = self.valid_request_handler_cls(req, resp)
        errors_handler = self.errors_handler_cls(req, resp)
        self.handle_request(req, valid_handler, errors_handler)

    def process_response(
        self, req: Request, resp: Response, resource: Any, req_succeeded: bool
    ) -> None:
        errors_handler = self.errors_handler_cls(req, resp)
        self.handle_response(req, resp, errors_handler)
