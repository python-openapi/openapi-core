import warnings
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.parameters.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.parameters.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.schema.parameters import get_aslist
from openapi_core.schema.parameters import get_explode
from openapi_core.spec import Spec


class CallableParameterDeserializer:
    def __init__(
        self,
        param_or_header: Spec,
        style: str,
        deserializer_callable: Optional[DeserializerCallable] = None,
    ):
        self.param_or_header = param_or_header
        self.style = style
        self.deserializer_callable = deserializer_callable

        self.aslist = get_aslist(self.param_or_header)
        self.explode = get_explode(self.param_or_header)

    def deserialize(self, value: Any) -> Any:
        if self.deserializer_callable is None:
            warnings.warn(f"Unsupported {self.style} style")
            return value

        # if "in" not defined then it's a Header
        if "allowEmptyValue" in self.param_or_header:
            warnings.warn(
                "Use of allowEmptyValue property is deprecated",
                DeprecationWarning,
            )
        allow_empty_values = self.param_or_header.getkey(
            "allowEmptyValue", False
        )
        location_name = self.param_or_header.getkey("in", "header")
        if location_name == "query" and value == "" and not allow_empty_values:
            name = self.param_or_header["name"]
            raise EmptyQueryParameterValue(name)

        if not self.aslist or self.explode:
            return value
        try:
            return self.deserializer_callable(value)
        except (ValueError, TypeError, AttributeError):
            raise DeserializeError(location_name, self.style, value)
