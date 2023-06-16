from typing import Any
from typing import Callable
from typing import Dict

FormatValidator = Callable[[Any], bool]

FormatValidatorsDict = Dict[str, FormatValidator]
