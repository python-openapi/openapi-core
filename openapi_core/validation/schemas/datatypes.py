from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple

from jsonschema_path import SchemaPath

FormatValidator = Callable[[Any], bool]

FormatValidatorsDict = Dict[str, FormatValidator]


@dataclass(frozen=True)
class ValidationState:
    schema: SchemaPath
    value: Any
    primitive_type: Optional[str] = None
    property_states: Dict[str, "ValidationState"] = field(default_factory=dict)
    additional_property_states: Dict[str, "ValidationState"] = field(
        default_factory=dict
    )
    item_states: Tuple["ValidationState", ...] = ()
    one_of_state: Optional["ValidationState"] = None
    any_of_states: Tuple["ValidationState", ...] = ()
    all_of_states: Tuple["ValidationState", ...] = ()


__all__ = ["FormatValidator", "FormatValidatorsDict", "ValidationState"]
