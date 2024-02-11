"""OpenAPI core contrib flask handlers module"""

from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Type

from flask.globals import current_app
from flask.helpers import make_response
from flask.json import dumps
from flask.wrappers import Request
from flask.wrappers import Response

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


class FlaskOpenAPIErrorsHandler:
    OPENAPI_ERROR_STATUS: Dict[Type[BaseException], int] = {
        ServerNotFound: 400,
        SecurityNotFound: 403,
        OperationNotFound: 405,
        PathNotFound: 404,
        MediaTypeNotFound: 415,
    }

    def __call__(self, errors: Iterable[Exception]) -> Response:
        data_errors = [self.format_openapi_error(err) for err in errors]
        data = {
            "errors": data_errors,
        }
        data_error_max = max(data_errors, key=self.get_error_status)
        status = data_error_max["status"]
        return current_app.response_class(
            dumps(data), status=status, mimetype="application/json"
        )

    @classmethod
    def format_openapi_error(cls, error: BaseException) -> Dict[str, Any]:
        if error.__cause__ is not None:
            error = error.__cause__
        return {
            "title": str(error),
            "status": cls.OPENAPI_ERROR_STATUS.get(error.__class__, 400),
            "class": str(type(error)),
        }

    @classmethod
    def get_error_status(cls, error: Dict[str, Any]) -> int:
        return int(error["status"])


class FlaskOpenAPIValidRequestHandler:
    def __init__(
        self,
        req: Request,
        view: Callable[[Any], Response],
        *view_args: Any,
        **view_kwargs: Any,
    ):
        self.req = req
        self.view = view
        self.view_args = view_args
        self.view_kwargs = view_kwargs

    def __call__(
        self, request_unmarshal_result: RequestUnmarshalResult
    ) -> Response:
        self.req.openapi = request_unmarshal_result  # type: ignore
        rv = self.view(*self.view_args, **self.view_kwargs)
        return make_response(rv)
