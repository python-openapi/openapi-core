"""OpenAPI core validation response datatypes module"""
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional

from openapi_core.validation.datatypes import BaseValidationResult


@dataclass
class ResponseValidationResult(BaseValidationResult):
    data: Optional[str] = None
    headers: Dict = field(default_factory=dict)
