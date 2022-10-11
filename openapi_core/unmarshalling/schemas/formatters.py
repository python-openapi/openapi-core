import warnings
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type


class Formatter:
    def validate(self, value: Any) -> bool:
        return True

    def format(self, value: Any) -> Any:
        return value

    def __getattribute__(self, name: str) -> Any:
        if name == "unmarshal":
            warnings.warn(
                "Unmarshal method is deprecated. " "Use format instead.",
                DeprecationWarning,
            )
            return super().__getattribute__("format")
        if name == "format":
            try:
                attr = super().__getattribute__("unmarshal")
            except AttributeError:
                return super().__getattribute__("format")
            else:
                warnings.warn(
                    "Unmarshal method is deprecated. "
                    "Rename unmarshal method to format instead.",
                    DeprecationWarning,
                )
                return attr
        return super().__getattribute__(name)

    @classmethod
    def from_callables(
        cls,
        validate_callable: Optional[Callable[[Any], Any]] = None,
        format_callable: Optional[Callable[[Any], Any]] = None,
        unmarshal: Optional[Callable[[Any], Any]] = None,
    ) -> "Formatter":
        attrs = {}
        if validate_callable is not None:
            attrs["validate"] = staticmethod(validate_callable)
        if format_callable is not None:
            attrs["format"] = staticmethod(format_callable)
        if unmarshal is not None:
            warnings.warn(
                "Unmarshal parameter is deprecated. "
                "Use format_callable instead.",
                DeprecationWarning,
            )
            attrs["format"] = staticmethod(unmarshal)

        klass: Type[Formatter] = type("Formatter", (cls,), attrs)
        return klass()
