from typing import Callable, Optional, TYPE_CHECKING, Union

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.spec.paths import SpecPath
if TYPE_CHECKING:
    from openapi_core.casting.schemas.factories import SchemaCastersFactory


class BaseSchemaCaster:

    def __init__(self, schema: SpecPath):
        self.schema = schema

    def __call__(
        self,
        value: Optional[Union[str, list, dict]],
    ) -> Optional[Union[int, float, bool, str, list, dict]]:
        if value is None:
            return value
        return self.cast(value)

    def cast(
        self,
        value: Union[str, list, dict],
    ) -> Union[int, float, bool, str, list, dict]:
        raise NotImplementedError


class CallableSchemaCaster(BaseSchemaCaster):

    def __init__(
        self,
        schema: SpecPath,
        caster_callable: Callable[[str], Union[int, float, bool]],
    ):
        super().__init__(schema)
        self.caster_callable = caster_callable

    def cast(
        self,
        value: Union[str, list, dict],
    ) -> Union[int, float, bool]:
        assert isinstance(value, str)
        try:
            return self.caster_callable(value)
        except (ValueError, TypeError):
            raise CastError(value, self.schema['type'])


class DummyCaster(BaseSchemaCaster):

    def cast(
        self,
        value: Union[str, list, dict],
    ) -> Union[str, list, dict]:
        return value


class ComplexCaster(BaseSchemaCaster):

    def __init__(
        self,
        schema: SpecPath,
        casters_factory: 'SchemaCastersFactory',
    ):
        super().__init__(schema)
        self.casters_factory = casters_factory


class ArrayCaster(ComplexCaster):

    @property
    def items_caster(self) -> BaseSchemaCaster:
        return self.casters_factory.create(self.schema / 'items')

    def cast(
        self,
        value: Union[str, list, dict],
    ) -> list:
        try:
            assert isinstance(value, list)
            return list(map(self.items_caster, value))
        except (AssertionError, ValueError, TypeError):
            raise CastError(value, self.schema['type'])
