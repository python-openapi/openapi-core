from enum import Enum


class DataKind(Enum):
    """Kind/nature of deserialized data.

    Describes whether data came from a typed deserializer that preserves
    runtime types, or from a string-based source that requires parsing.

    Attributes:
        TYPED: Data from a typed deserializer (JSON, MessagePack, etc.).
            Values are already properly typed (int, float, bool, None, dict, list).
        STRINGLY: Data from string-based encoding (forms, params, headers).
            Values are strings/bytes that need parsing/coercion to match schema types.
    """

    TYPED = "typed"
    STRINGLY = "stringly"
