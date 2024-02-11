"""OpenAPI core contrib starlette handlers module"""

from typing import Any
from typing import Dict
from typing import Iterable
from typing import Type

from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import Response

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


class StarletteOpenAPIErrorsHandler:
    OPENAPI_ERROR_STATUS: Dict[Type[BaseException], int] = {
        ServerNotFound: 400,
        SecurityNotFound: 403,
        OperationNotFound: 405,
        PathNotFound: 404,
        MediaTypeNotFound: 415,
    }

    def __call__(
        self,
        errors: Iterable[Exception],
    ) -> JSONResponse:
        data_errors = [self.format_openapi_error(err) for err in errors]
        data = {
            "errors": data_errors,
        }
        data_error_max = max(data_errors, key=self.get_error_status)
        return JSONResponse(data, status_code=data_error_max["status"])

    @classmethod
    def format_openapi_error(cls, error: BaseException) -> Dict[str, Any]:
        if error.__cause__ is not None:
            error = error.__cause__
        return {
            "title": str(error),
            "status": cls.OPENAPI_ERROR_STATUS.get(error.__class__, 400),
            "type": str(type(error)),
        }

    @classmethod
    def get_error_status(cls, error: Dict[str, Any]) -> str:
        return str(error["status"])


class StarletteOpenAPIValidRequestHandler:
    def __init__(self, request: Request, call_next: RequestResponseEndpoint):
        self.request = request
        self.call_next = call_next

    async def __call__(
        self, request_unmarshal_result: RequestUnmarshalResult
    ) -> Response:
        self.request.scope["openapi"] = request_unmarshal_result
        return await self.call_next(self.request)
