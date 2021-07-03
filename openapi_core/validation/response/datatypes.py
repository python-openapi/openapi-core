"""OpenAPI core validation response datatypes module"""
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional

from werkzeug.datastructures import Headers

from openapi_core.validation.datatypes import BaseValidationResult


@dataclass
class OpenAPIResponse:
    """OpenAPI request dataclass.

    Attributes:
        data
            The response body, as string.
        status_code
            The status code as integer.
        headers
            Response headers as Headers.
        mimetype
            Lowercase content type without charset.
    """

    data: str
    status_code: int
    mimetype: str
    headers: Headers = field(default_factory=Headers)


@dataclass
class ResponseValidationResult(BaseValidationResult):
    data: Optional[str] = None
    headers: Dict = field(default_factory=dict)
