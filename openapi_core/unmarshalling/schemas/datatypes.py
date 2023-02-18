from typing import Any
from typing import Callable
from typing import Dict

FormatUnmarshaller = Callable[[Any], Any]
FormatUnmarshallersDict = Dict[str, FormatUnmarshaller]
