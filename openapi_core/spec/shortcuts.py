"""OpenAPI core spec shortcuts module"""
from typing import Any
from typing import Dict
from typing import Hashable
from typing import Mapping
from typing import Optional

from jsonschema_spec import default_handlers
from openapi_spec_validator.validation import openapi_spec_validator_proxy
from openapi_spec_validator.validation.protocols import SupportsValidation

from openapi_core.spec.paths import Spec


def create_spec(
    spec_dict: Mapping[Hashable, Any],
    spec_url: str = "",
    handlers: Dict[str, Any] = default_handlers,
    validate_spec: bool = True,
) -> Spec:
    validator: Optional[SupportsValidation] = None
    if validate_spec:
        validator = openapi_spec_validator_proxy

    return Spec.create(
        spec_dict,
        url=spec_url,
        ref_resolver_handlers=handlers,
        validator=validator,
    )
