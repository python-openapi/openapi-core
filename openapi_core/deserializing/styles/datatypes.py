from typing import Any
from typing import Callable
from typing import Dict
from typing import Mapping

DeserializerCallable = Callable[[bool, str, str, Mapping[str, Any]], Any]
StyleDeserializersDict = Dict[str, DeserializerCallable]
