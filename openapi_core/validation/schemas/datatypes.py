from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional

from openapi_core.validation.schemas.formatters import Formatter

FormatValidator = Callable[[Any], bool]

CustomFormattersDict = Dict[str, Formatter]
FormattersDict = Dict[Optional[str], Formatter]
FormatValidatorsDict = Dict[str, FormatValidator]
