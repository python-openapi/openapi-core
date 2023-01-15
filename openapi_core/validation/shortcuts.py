"""OpenAPI core validation shortcuts module"""
import warnings
from typing import Any
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import Type

from openapi_core.spec import Spec
from openapi_core.validation.exceptions import ValidatorDetectError
from openapi_core.validation.request import V30RequestValidator
from openapi_core.validation.request import V31RequestValidator
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.proxies import SpecRequestValidatorProxy
from openapi_core.validation.response import V30ResponseValidator
from openapi_core.validation.response import V31ResponseValidator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.proxies import SpecResponseValidatorProxy


class SpecVersion(NamedTuple):
    name: str
    version: str


class SpecValidators(NamedTuple):
    request: Type[RequestValidator]
    response: Type[ResponseValidator]


SPECS: Dict[SpecVersion, SpecValidators] = {
    SpecVersion("openapi", "3.0"): SpecValidators(
        V30RequestValidator, V30ResponseValidator
    ),
    SpecVersion("openapi", "3.1"): SpecValidators(
        V31RequestValidator, V31ResponseValidator
    ),
}


def get_validators(spec: Spec) -> SpecValidators:
    for v, validators in SPECS.items():
        if v.name in spec and spec[v.name].startswith(v.version):
            return validators
    raise ValidatorDetectError("Spec schema version not detected")


def validate_request(
    request: Request,
    spec: Spec,
    base_url: Optional[str] = None,
    validator: Optional[SpecRequestValidatorProxy] = None,
    cls: Optional[Type[RequestValidator]] = None,
    **validator_kwargs: Any,
) -> RequestValidationResult:
    if validator is not None:
        warnings.warn(
            "validator parameter is deprecated. Use cls instead.",
            DeprecationWarning,
        )
        result = validator.validate(spec, request, base_url=base_url)
    else:
        if cls is None:
            validators = get_validators(spec)
            cls = getattr(validators, "request")
        v = cls(spec, base_url=base_url, **validator_kwargs)
        result = v.validate(request)
    result.raise_for_errors()
    return result


def validate_response(
    request: Request,
    response: Response,
    spec: Spec,
    base_url: Optional[str] = None,
    validator: Optional[SpecResponseValidatorProxy] = None,
    cls: Optional[Type[ResponseValidator]] = None,
    **validator_kwargs: Any,
) -> ResponseValidationResult:
    if validator is not None:
        warnings.warn(
            "validator parameter is deprecated. Use cls instead.",
            DeprecationWarning,
        )
        result = validator.validate(spec, request, response, base_url=base_url)
    else:
        if cls is None:
            validators = get_validators(spec)
            cls = getattr(validators, "response")
        v = cls(spec, base_url=base_url, **validator_kwargs)
        result = v.validate(request, response)
    result.raise_for_errors()
    return result
