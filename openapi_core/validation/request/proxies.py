"""OpenAPI spec validator validation proxies module."""
import warnings
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import Type

from openapi_core.spec import Spec
from openapi_core.validation.exceptions import ValidatorDetectError
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.validators import (
    BaseAPICallRequestValidator,
)


class SpecRequestValidatorProxy:
    def __init__(
        self,
        validator_cls: Type[BaseAPICallRequestValidator],
        **validator_kwargs: Any,
    ):
        self.validator_cls = validator_cls
        self.validator_kwargs = validator_kwargs

    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        warnings.warn(
            "openapi_request_validator is deprecated. "
            f"Use {self.validator_cls.__name__} class instead.",
            DeprecationWarning,
        )
        validator = self.validator_cls(
            spec, base_url=base_url, **self.validator_kwargs
        )
        return validator.validate(request)

    def is_valid(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> bool:
        validator = self.validator_cls(
            spec, base_url=base_url, **self.validator_kwargs
        )
        error = next(validator.iter_errors(request), None)
        return error is None

    def iter_errors(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> Iterator[Exception]:
        validator = self.validator_cls(
            spec, base_url=base_url, **self.validator_kwargs
        )
        yield from validator.iter_errors(request)


class DetectSpecRequestValidatorProxy:
    def __init__(
        self, choices: Mapping[Tuple[str, str], SpecRequestValidatorProxy]
    ):
        self.choices = choices

    def detect(self, spec: Spec) -> SpecRequestValidatorProxy:
        for (key, value), validator in self.choices.items():
            if key in spec and spec[key].startswith(value):
                return validator
        raise ValidatorDetectError("Spec schema version not detected")

    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        validator = self.detect(spec)
        return validator.validate(spec, request, base_url=base_url)

    def is_valid(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> bool:
        validator = self.detect(spec)
        error = next(
            validator.iter_errors(spec, request, base_url=base_url), None
        )
        return error is None

    def iter_errors(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> Iterator[Exception]:
        validator = self.detect(spec)
        yield from validator.iter_errors(spec, request, base_url=base_url)
