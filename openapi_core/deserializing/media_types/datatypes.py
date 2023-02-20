from typing import Any
from typing import Callable
from typing import Dict

DeserializerCallable = Callable[[Any], Any]
MediaTypeDeserializersDict = Dict[str, DeserializerCallable]
