"""OpenAPI core contrib flask handlers module"""
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Type

from flask.globals import current_app
from flask.json import dumps
from flask.wrappers import Response

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound
from openapi_core.templating.paths.exceptions import OperationNotFound
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.paths.exceptions import ServerNotFound
from openapi_core.templating.security.exceptions import SecurityNotFound


class FlaskOpenAPIErrorsHandler:
    OPENAPI_ERROR_STATUS: Dict[Type[BaseException], int] = {
        ServerNotFound: 400,
        SecurityNotFound: 403,
        OperationNotFound: 405,
        PathNotFound: 404,
        MediaTypeNotFound: 415,
    }

    @classmethod
    def handle(cls, errors: Iterable[BaseException]) -> Response:
        data_errors = [cls.format_openapi_error(err) for err in errors]
        data = {
            "errors": data_errors,
        }
        data_error_max = max(data_errors, key=cls.get_error_status)
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
