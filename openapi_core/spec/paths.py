from typing import Any
from typing import Dict
from typing import Hashable
from typing import Mapping
from typing import Type
from typing import TypeVar

from jsonschema.protocols import Validator
from jsonschema_spec import Spec as JsonschemaSpec
from jsonschema_spec import default_handlers
from openapi_spec_validator import openapi_v30_spec_validator

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
        validator: Validator = openapi_v30_spec_validator,
    ) -> TSpec:
        if validator is not None:
            validator.validate(data, spec_url=url)

        return cls.from_dict(
            data,
            *args,
            spec_url=url,
            ref_resolver_handlers=ref_resolver_handlers,
            separator=separator,
        )
