from typing import Dict
from typing import Optional

from openapi_core.unmarshalling.schemas.formatters import Formatter

CustomFormattersDict = Dict[str, Formatter]
FormattersDict = Dict[Optional[str], Formatter]
