"""OpenAPI core validation exceptions module"""

from dataclasses import dataclass
from typing import Any

from openapi_core.exceptions import OpenAPIError


def _schema_error_to_dict(schema_error: Exception) -> dict[str, Any]:
    message = getattr(schema_error, "message", str(schema_error))
    raw_path = getattr(schema_error, "path", ())
    try:
        path = list(raw_path)
    except TypeError:
        path = []
    return {
        "message": message,
        "path": path,
    }


@dataclass
class ValidationError(OpenAPIError):
    @property
    def details(self) -> dict[str, Any]:
        cause = self.__cause__
        schema_errors: list[dict[str, Any]] = []
        if cause is not None:
            cause_schema_errors = getattr(cause, "schema_errors", None)
            if cause_schema_errors is not None:
                schema_errors = [
                    _schema_error_to_dict(schema_error)
                    for schema_error in cause_schema_errors
                ]

        return {
            "message": str(self),
            "error_type": self.__class__.__name__,
            "cause_type": (
                cause.__class__.__name__ if cause is not None else None
            ),
            "schema_errors": schema_errors,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.__cause__}"
