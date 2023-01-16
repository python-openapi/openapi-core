import warnings
from typing import Any
from typing import Dict
from typing import Hashable
from typing import Mapping
from typing import Optional
from typing import Type
from typing import TypeVar

from jsonschema_spec import Spec as JsonschemaSpec
from jsonschema_spec import default_handlers
from openapi_spec_validator.validation import openapi_spec_validator_proxy
from openapi_spec_validator.validation.protocols import SupportsValidation

TSpec = TypeVar("TSpec", bound="Spec")

SPEC_SEPARATOR = "#"


class Spec(JsonschemaSpec):
    @classmethod
    def create(
        cls: Type[TSpec],
        data: Mapping[Hashable, Any],
        *args: Any,
        url: str = "",
        ref_resolver_handlers: Dict[str, Any] = default_handlers,
        separator: str = SPEC_SEPARATOR,
        validator: Optional[SupportsValidation] = openapi_spec_validator_proxy,
    ) -> TSpec:
        warnings.warn(
            "Spec.create method is deprecated. Use Spec.from_dict instead.",
            DeprecationWarning,
        )

        return cls.from_dict(
            data,
            *args,
            spec_url=url,
            ref_resolver_handlers=ref_resolver_handlers,
            separator=separator,
            validator=validator,
        )

    @classmethod
    def from_dict(
        cls: Type[TSpec],
        data: Mapping[Hashable, Any],
        *args: Any,
        spec_url: str = "",
        ref_resolver_handlers: Mapping[str, Any] = default_handlers,
        separator: str = SPEC_SEPARATOR,
        validator: Optional[SupportsValidation] = openapi_spec_validator_proxy,
    ) -> TSpec:
        if validator is not None:
            validator.validate(data, spec_url=spec_url)

        return super().from_dict(
            data,
            *args,
            spec_url=spec_url,
            ref_resolver_handlers=ref_resolver_handlers,
            separator=separator,
        )
