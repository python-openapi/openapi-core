from typing import Any
from typing import Callable
from typing import Optional
from typing import Type


class Formatter:
    def validate(self, value: Any) -> bool:
        return True

    def format(self, value: Any) -> Any:
        return value

    @classmethod
    def from_callables(
        cls,
        validate_callable: Optional[Callable[[Any], Any]] = None,
        format_callable: Optional[Callable[[Any], Any]] = None,
    ) -> "Formatter":
        attrs = {}
        if validate_callable is not None:
            attrs["validate"] = staticmethod(validate_callable)
        if format_callable is not None:
            attrs["format"] = staticmethod(format_callable)

        klass: Type[Formatter] = type("Formatter", (cls,), attrs)
        return klass()
