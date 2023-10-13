import warnings
from typing import Any
from typing import Hashable
from typing import Mapping
from typing import Type
from typing import TypeVar

from jsonschema_path import SchemaPath
from openapi_spec_validator.validation import openapi_spec_validator_proxy

TSpec = TypeVar("TSpec", bound="Spec")

SPEC_SEPARATOR = "#"


class Spec(SchemaPath):
    @classmethod
    def from_dict(
        cls: Type[TSpec],
        data: Mapping[Hashable, Any],
        *args: Any,
        **kwargs: Any,
    ) -> TSpec:
        warnings.warn(
            "Spec is deprecated. Use SchemaPath from jsonschema-path package.",
            DeprecationWarning,
        )
        validator = kwargs.pop("validator", openapi_spec_validator_proxy)
        if validator is not None:
            base_uri = kwargs.get("base_uri", "")
            spec_url = kwargs.get("spec_url")
            validator.validate(data, base_uri=base_uri, spec_url=spec_url)

        return super().from_dict(data, *args, **kwargs)
