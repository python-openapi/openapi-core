"""OpenAPI core contrib django handlers module"""
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Type

from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.exceptions import MissingRequiredParameter


class DjangoOpenAPIErrorsHandler:

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
        cls,
        errors: Iterable[Exception],
        req: HttpRequest,
        resp: Optional[HttpResponse] = None,
    ) -> JsonResponse:
        data_errors = [cls.format_openapi_error(err) for err in errors]
        data = {
            "errors": data_errors,
        }
        data_error_max = max(data_errors, key=cls.get_error_status)
        return JsonResponse(data, status=data_error_max["status"])

    @classmethod
    def format_openapi_error(cls, error: Exception) -> Dict[str, Any]:
        return {
            "title": str(error),
            "status": cls.OPENAPI_ERROR_STATUS.get(error.__class__, 400),
            "type": str(type(error)),
        }

    @classmethod
    def get_error_status(cls, error: Dict[str, Any]) -> str:
        return str(error["status"])
