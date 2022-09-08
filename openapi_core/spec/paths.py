from typing import Any
from typing import Dict
from typing import Hashable
from typing import Mapping

from jsonschema.protocols import Validator
from jsonschema.validators import RefResolver
from openapi_spec_validator import default_handlers
from openapi_spec_validator import openapi_v3_spec_validator
from openapi_spec_validator.validators import Dereferencer
from pathable.paths import AccessorPath

from openapi_core.spec.accessors import SpecAccessor

SPEC_SEPARATOR = "#"


class Spec(AccessorPath):
    @classmethod
    def from_dict(
        cls,
        data: Mapping[Hashable, Any],
        *args: Any,
        url: str = "",
        ref_resolver_handlers: Dict[str, Any] = default_handlers,
        separator: str = SPEC_SEPARATOR,
    ) -> "Spec":
        ref_resolver = RefResolver(url, data, handlers=ref_resolver_handlers)
        dereferencer = Dereferencer(ref_resolver)
        accessor = SpecAccessor(data, dereferencer)
        return cls(accessor, *args, separator=separator)

    @classmethod
    def create(
        cls,
        data: Mapping[Hashable, Any],
        *args: Any,
        url: str = "",
        ref_resolver_handlers: Dict[str, Any] = default_handlers,
        separator: str = SPEC_SEPARATOR,
        validator: Validator = openapi_v3_spec_validator,
    ) -> "Spec":
        if validator is not None:
            validator.validate(data, spec_url=url)

        return cls.from_dict(
            data,
            *args,
            url=url,
            ref_resolver_handlers=ref_resolver_handlers,
            separator=separator,
        )
