"""OpenAPI core validation datatypes module"""
from typing import Sequence, Union

from dataclasses import dataclass

from openapi_core.validation.types import ValidationErrors


@dataclass
class BaseValidationResult:
    errors: Sequence[ValidationErrors]

    def raise_for_errors(self):
        for error in self.errors:
            raise error
