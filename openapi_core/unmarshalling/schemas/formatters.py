from typing import Any
from typing import Callable
from typing import Optional
from typing import Type


class Formatter:
    def validate(self, value: Any) -> bool:
        return True

    def unmarshal(self, value: Any) -> Any:
        return value

    @classmethod
    def from_callables(
        cls,
        validate: Optional[Callable[[Any], Any]] = None,
        unmarshal: Optional[Callable[[Any], Any]] = None,
    ) -> "Formatter":
        attrs = {}
        if validate is not None:
            attrs["validate"] = staticmethod(validate)
        if unmarshal is not None:
            attrs["unmarshal"] = staticmethod(unmarshal)

        klass: Type[Formatter] = type("Formatter", (cls,), attrs)
        return klass()
