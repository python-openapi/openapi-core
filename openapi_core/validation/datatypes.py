"""OpenAPI core validation datatypes module"""
from dataclasses import dataclass
from typing import List


@dataclass
class BaseValidationResult:
    errors: List[Exception]

    def raise_for_errors(self):
        for error in self.errors:
            raise error
