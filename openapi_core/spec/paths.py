import warnings
from typing import Any

from jsonschema_path import SchemaPath


class Spec(SchemaPath):
    def __init__(self, *args: Any, **kwargs: Any):
        warnings.warn(
            "Spec is deprecated. Use SchemaPath from jsonschema-path package.",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
