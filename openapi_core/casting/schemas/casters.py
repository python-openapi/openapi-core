from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import List

from openapi_core.casting.schemas.datatypes import CasterCallable
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.spec import Spec

if TYPE_CHECKING:
    from openapi_core.casting.schemas.factories import SchemaCastersFactory


class BaseSchemaCaster:
    def __init__(self, schema: Spec):
        self.schema = schema

    def __call__(self, value: Any) -> Any:
        if value is None:
            return value

        return self.cast(value)

    def cast(self, value: Any) -> Any:
        raise NotImplementedError


class CallableSchemaCaster(BaseSchemaCaster):
    def __init__(self, schema: Spec, caster_callable: CasterCallable):
        super().__init__(schema)
        self.caster_callable = caster_callable

    def cast(self, value: Any) -> Any:
        try:
            return self.caster_callable(value)
        except (ValueError, TypeError):
            raise CastError(value, self.schema["type"])


class DummyCaster(BaseSchemaCaster):
    def cast(self, value: Any) -> Any:
        return value


class ComplexCaster(BaseSchemaCaster):
    def __init__(self, schema: Spec, casters_factory: "SchemaCastersFactory"):
        super().__init__(schema)
        self.casters_factory = casters_factory


class ArrayCaster(ComplexCaster):
    @property
    def items_caster(self) -> BaseSchemaCaster:
        return self.casters_factory.create(self.schema / "items")

    def cast(self, value: Any) -> List[Any]:
        # str and bytes are not arrays according to the OpenAPI spec
        if isinstance(value, (str, bytes)):
            raise CastError(value, self.schema["type"])

        try:
            return list(map(self.items_caster, value))
        except (ValueError, TypeError):
            raise CastError(value, self.schema["type"])
