"""OpenAPI core unmarshalling request datatypes module"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from openapi_core.datatypes import Parameters
from openapi_core.unmarshalling.datatypes import BaseUnmarshalResult


@dataclass
class RequestUnmarshalResult(BaseUnmarshalResult):
    body: str | None = None
    parameters: Parameters = field(default_factory=Parameters)
    security: dict[str, str] | None = None
