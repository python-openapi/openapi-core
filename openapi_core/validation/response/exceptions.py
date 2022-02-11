from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List


@dataclass
class HeadersError(Exception):
    headers: Dict[str, Any]
    context: List[Exception]
