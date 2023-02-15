"""OpenAPI core validation datatypes module"""
from dataclasses import dataclass
from typing import Iterable

from openapi_core.exceptions import OpenAPIError


@dataclass
class BaseUnmarshalResult:
    errors: Iterable[OpenAPIError]

    def raise_for_errors(self) -> None:
        for error in self.errors:
            raise error
