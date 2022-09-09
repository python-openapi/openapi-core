"""OpenAPI core spec shortcuts module"""
from typing import Any
from typing import Dict
from typing import Hashable
from typing import Mapping

from jsonschema.validators import RefResolver
from openapi_spec_validator import default_handlers
from openapi_spec_validator import openapi_v3_spec_validator
from openapi_spec_validator.validators import Dereferencer

from openapi_core.spec.paths import Spec


def create_spec(
    spec_dict: Mapping[Hashable, Any],
    spec_url: str = "",
    handlers: Dict[str, Any] = default_handlers,
    validate_spec: bool = True,
) -> Spec:
    validator = None
    if validate_spec:
        validator = openapi_v3_spec_validator

    return Spec.create(
        spec_dict,
        url=spec_url,
        ref_resolver_handlers=handlers,
        validator=validator,
    )
