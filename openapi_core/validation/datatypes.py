"""OpenAPI core validation datatypes module"""
from typing import List

from dataclasses import dataclass


@dataclass
class BaseValidationResult:
    errors: List[Exception]

    def raise_for_errors(self):
        for error in self.errors:
            raise error
