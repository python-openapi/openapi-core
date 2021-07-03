"""OpenAPI core validation request datatypes module"""
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.validation.datatypes import BaseValidationResult


@dataclass
class RequestParameters:
    """OpenAPI request parameters dataclass.

    Attributes:
        query
            Query string parameters as MultiDict. Must support getlist method.
        header
            Request headers as Headers.
        cookie
            Request cookies as MultiDict.
        path
            Path parameters as dict. Gets resolved against spec if empty.
    """

    query: ImmutableMultiDict = field(default_factory=ImmutableMultiDict)
    header: Headers = field(default_factory=Headers)
    cookie: ImmutableMultiDict = field(default_factory=ImmutableMultiDict)
    path: Dict = field(default_factory=dict)

    def __getitem__(self, location):
        return getattr(self, location)


@dataclass
class OpenAPIRequest:
    """OpenAPI request dataclass.

    Attributes:
        full_url_pattern
            The matched url with scheme, host and path pattern.
            For example:
            https://localhost:8000/api/v1/pets
            https://localhost:8000/api/v1/pets/{pet_id}
        method
            The request method, as lowercase string.
        parameters
            A RequestParameters object.
        body
            The request body, as string.
        mimetype
            Like content type, but without parameters (eg, without charset,
            type etc.) and always lowercase.
            For example if the content type is "text/HTML; charset=utf-8"
            the mimetype would be "text/html".
    """

    full_url_pattern: str
    method: str
    body: str
    mimetype: str
    parameters: RequestParameters = field(default_factory=RequestParameters)


@dataclass
class Parameters:
    query: Dict = field(default_factory=dict)
    header: Dict = field(default_factory=dict)
    cookie: Dict = field(default_factory=dict)
    path: Dict = field(default_factory=dict)


@dataclass
class RequestValidationResult(BaseValidationResult):
    body: Optional[str] = None
    parameters: Parameters = field(default_factory=Parameters)
    security: Optional[Dict[str, str]] = None
