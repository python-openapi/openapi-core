"""OpenAPI core validation datatypes module"""
from dataclasses import dataclass
from typing import Iterable


@dataclass
class BaseValidationResult:
    errors: Iterable[Exception]

    def raise_for_errors(self) -> None:
        for error in self.errors:
            raise error
