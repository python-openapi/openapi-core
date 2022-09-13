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
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.exceptions import MissingRequiredParameter


class FalconOpenAPIErrorsHandler:

    OPENAPI_ERROR_STATUS: Dict[Type[Exception], int] = {
        MissingRequiredParameter: 400,
        ServerNotFound: 400,
        InvalidSecurity: 403,
        OperationNotFound: 405,
        PathNotFound: 404,
        MediaTypeNotFound: 415,
    }

    @classmethod
    def handle(
        cls, req: Request, resp: Response, errors: Iterable[Exception]
    ) -> None:
        data_errors = [cls.format_openapi_error(err) for err in errors]
        data = {
            "errors": data_errors,
        }
        data_str = dumps(data)
        data_error_max = max(data_errors, key=cls.get_error_status)
        resp.content_type = MEDIA_JSON
        resp.status = getattr(
            status_codes,
            f"HTTP_{data_error_max['status']}",
            status_codes.HTTP_400,
        )
        resp.text = data_str
        resp.complete = True

    @classmethod
    def format_openapi_error(cls, error: Exception) -> Dict[str, Any]:
        return {
            "title": str(error),
            "status": cls.OPENAPI_ERROR_STATUS.get(error.__class__, 400),
            "type": str(type(error)),
        }

    @classmethod
    def get_error_status(cls, error: Dict[str, Any]) -> int:
        return int(error["status"])
