"""OpenAPI core unmarshalling response datatypes module"""
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Optional

from openapi_core.unmarshalling.datatypes import BaseUnmarshalResult


@dataclass
class ResponseUnmarshalResult(BaseUnmarshalResult):
    data: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
