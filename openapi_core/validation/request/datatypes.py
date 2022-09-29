"""OpenAPI core validation request datatypes module"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping

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

    query: Mapping[str, Any] = field(default_factory=ImmutableMultiDict)
    header: Mapping[str, Any] = field(default_factory=Headers)
    cookie: Mapping[str, Any] = field(default_factory=ImmutableMultiDict)
    path: Mapping[str, Any] = field(default_factory=dict)

    def __getitem__(self, location: str) -> Any:
        return getattr(self, location)


@dataclass
class Parameters:
    query: Mapping[str, Any] = field(default_factory=dict)
    header: Mapping[str, Any] = field(default_factory=dict)
    cookie: Mapping[str, Any] = field(default_factory=dict)
    path: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class RequestValidationResult(BaseValidationResult):
    body: str | None = None
    parameters: Parameters = field(default_factory=Parameters)
    security: dict[str, str] | None = None
