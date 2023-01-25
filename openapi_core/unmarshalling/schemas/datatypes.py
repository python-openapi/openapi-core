from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional

from openapi_core.unmarshalling.schemas.formatters import Formatter

CustomFormattersDict = Dict[str, Formatter]
FormattersDict = Dict[Optional[str], Formatter]
UnmarshallersDict = Dict[str, Callable[[Any], Any]]
