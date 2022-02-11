from dataclasses import dataclass
from typing import List

from openapi_core.validation.request.datatypes import Parameters


@dataclass
class ParametersError(Exception):
    parameters: Parameters
    context: List[Exception]
