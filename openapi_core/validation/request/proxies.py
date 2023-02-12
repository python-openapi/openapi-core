"""OpenAPI spec validator validation proxies module."""
import warnings
from typing import TYPE_CHECKING
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

if TYPE_CHECKING:
    from openapi_core.validation.request.validators import (
        BaseAPICallRequestValidator,
    )


class SpecRequestValidatorProxy:
    def __init__(
        self,
        unmarshaller_cls_name: str,
        deprecated: str = "RequestValidator",
        use: Optional[str] = None,
        **unmarshaller_kwargs: Any,
    ):
        self.unmarshaller_cls_name = unmarshaller_cls_name
        self.unmarshaller_kwargs = unmarshaller_kwargs

        self.deprecated = deprecated
        self.use = use or self.unmarshaller_cls_name

    @property
    def unmarshaller_cls(self) -> Type["BaseAPICallRequestValidator"]:
        from openapi_core.unmarshalling.request import unmarshallers

        return getattr(unmarshallers, self.unmarshaller_cls_name)

    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        warnings.warn(
            f"{self.deprecated} is deprecated. Use {self.use} instead.",
            DeprecationWarning,
        )
        unmarshaller = self.unmarshaller_cls(
            spec, base_url=base_url, **self.unmarshaller_kwargs
        )
        return unmarshaller.validate(request)

    def is_valid(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> bool:
        unmarshaller = self.unmarshaller_cls(
            spec, base_url=base_url, **self.unmarshaller_kwargs
        )
        error = next(unmarshaller.iter_errors(request), None)
        return error is None

    def iter_errors(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> Iterator[Exception]:
        unmarshaller = self.unmarshaller_cls(
            spec, base_url=base_url, **self.unmarshaller_kwargs
        )
        yield from unmarshaller.iter_errors(request)


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
