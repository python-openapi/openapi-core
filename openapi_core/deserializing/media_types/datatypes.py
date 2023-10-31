from typing import Any
from typing import Callable
from typing import Dict

DeserializerCallable = Callable[[bytes], Any]
MediaTypeDeserializersDict = Dict[str, DeserializerCallable]
