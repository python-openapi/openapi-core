from dataclasses import dataclass
from dataclasses import field
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Dict
from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath

FormatValidator = Callable[[Any], bool]

FormatValidatorsDict = Dict[str, FormatValidator]


# Shared, read-only "empty container" singletons used as the default
# values for ValidationState collection fields. Because ValidationState
# is frozen these are safe to share across instances -- there is no
# code path that mutates the fields after construction. Using a single
# empty mapping/tuple instead of allocating a fresh dict/() for every
# leaf state cuts the per-instance allocation count from ~5 to 1.
_EMPTY_STATES: Mapping[str, "ValidationState"] = MappingProxyType({})
_EMPTY_STATE_TUPLE: tuple["ValidationState", ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationState:
    """The result of validating ``value`` against ``schema``.

    Carries forward two pieces of information that the unmarshaller
    would otherwise have to recompute:

    1. The fact that ``value`` was validated -- so child unmarshallers
       can skip re-running ``validate()`` against the same value.
    2. Which composed schemas matched (``one_of_state``,
       ``any_of_states``, ``all_of_states``) -- so the unmarshaller
       doesn't have to re-resolve ``oneOf`` / ``anyOf`` / ``allOf``
       branch selection at unmarshal time.

    State is only built for sub-trees that actually carry one of these
    two pieces of information. Sub-trees with no composition anywhere
    don't get a populated state; the unmarshaller takes a fast bare-
    state path for them. See ``SchemaValidator._schema_needs_state``.
    """

    schema: SchemaPath
    value: Any
    primitive_type: Optional[str] = None
    property_states: Mapping[str, "ValidationState"] = field(
        default_factory=lambda: _EMPTY_STATES,
    )
    additional_property_states: Mapping[str, "ValidationState"] = field(
        default_factory=lambda: _EMPTY_STATES,
    )
    item_states: tuple["ValidationState", ...] = _EMPTY_STATE_TUPLE
    one_of_state: Optional["ValidationState"] = None
    any_of_states: tuple["ValidationState", ...] = _EMPTY_STATE_TUPLE
    all_of_states: tuple["ValidationState", ...] = _EMPTY_STATE_TUPLE


__all__ = ["FormatValidator", "FormatValidatorsDict", "ValidationState"]
