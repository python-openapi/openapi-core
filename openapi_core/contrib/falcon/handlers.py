"""OpenAPI core contrib falcon handlers module"""

from json import dumps
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Type

from falcon import status_codes
from falcon.constants import MEDIA_JSON
from falcon.request import Request
from falcon.response import Response

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


class FalconOpenAPIErrorsHandler:
    OPENAPI_ERROR_STATUS: Dict[Type[BaseException], int] = {
        ServerNotFound: 400,
        SecurityNotFound: 403,
        OperationNotFound: 405,
        PathNotFound: 404,
        MediaTypeNotFound: 415,
    }

    def __init__(self, req: Request, resp: Response):
        self.req = req
        self.resp = resp

    def __call__(self, errors: Iterable[Exception]) -> Response:
        data_errors = [self.format_openapi_error(err) for err in errors]
        data = {
            "errors": data_errors,
        }
        data_str = dumps(data)
        data_error_max = max(data_errors, key=self.get_error_status)
        self.resp.content_type = MEDIA_JSON
        self.resp.status = getattr(
            status_codes,
            f"HTTP_{data_error_max['status']}",
            status_codes.HTTP_400,
        )
        self.resp.text = data_str
        self.resp.complete = True
        return self.resp

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
    def get_error_status(cls, error: Dict[str, Any]) -> int:
        return int(error["status"])


class FalconOpenAPIValidRequestHandler:
    def __init__(self, req: Request, resp: Response):
        self.req = req
        self.resp = resp

    def __call__(
        self, request_unmarshal_result: RequestUnmarshalResult
    ) -> Response:
        self.req.context.openapi = request_unmarshal_result
        return self.resp
