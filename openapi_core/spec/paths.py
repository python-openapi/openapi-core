import warnings
from typing import Any
from typing import Hashable
from typing import Mapping
from typing import Type
from typing import TypeVar

from jsonschema.validators import _UNSET
from jsonschema_path import SchemaPath
from openapi_spec_validator import validate

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
        if "validator" in kwargs:
            warnings.warn(
                "validator parameter is deprecated. Use spec_validator_cls instead.",
                DeprecationWarning,
            )
        validator = kwargs.pop("validator", _UNSET)
        spec_validator_cls = kwargs.pop("spec_validator_cls", _UNSET)
        base_uri = kwargs.get("base_uri", "")
        spec_url = kwargs.get("spec_url")
        if spec_validator_cls is not None:
            if spec_validator_cls is not _UNSET:
                validate(data, base_uri=base_uri, cls=spec_validator_cls)
            elif validator is _UNSET:
                validate(data, base_uri=base_uri)
            elif validator is not None:
                validator.validate(data, base_uri=base_uri, spec_url=spec_url)

        return super().from_dict(data, *args, **kwargs)
