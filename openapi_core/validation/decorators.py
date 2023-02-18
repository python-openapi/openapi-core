from functools import wraps
from inspect import signature
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type

from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.schemas.exceptions import ValidateError

OpenAPIErrorType = Type[OpenAPIError]


class ValidationErrorWrapper:
    def __init__(
        self,
        err_cls: OpenAPIErrorType,
        err_validate_cls: Optional[OpenAPIErrorType] = None,
        err_cls_init: Optional[str] = None,
        **err_cls_kw: Any
    ):
        self.err_cls = err_cls
        self.err_validate_cls = err_validate_cls or err_cls
        self.err_cls_init = err_cls_init
        self.err_cls_kw = err_cls_kw

    def __call__(self, f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper(*args: Any, **kwds: Any) -> Any:
            try:
                return f(*args, **kwds)
            except ValidateError as exc:
                self._raise_error(exc, self.err_validate_cls, f, *args, **kwds)
            except OpenAPIError as exc:
                self._raise_error(exc, self.err_cls, f, *args, **kwds)

        return wrapper

    def _raise_error(
        self,
        exc: OpenAPIError,
        cls: OpenAPIErrorType,
        f: Callable[..., Any],
        *args: Any,
        **kwds: Any
    ) -> None:
        if isinstance(exc, self.err_cls):
            raise
        sig = signature(f)
        ba = sig.bind(*args, **kwds)
        kw = {
            name: ba.arguments[func_kw]
            for name, func_kw in self.err_cls_kw.items()
        }
        init = cls
        if self.err_cls_init is not None:
            init = getattr(cls, self.err_cls_init)
        raise init(**kw) from exc
