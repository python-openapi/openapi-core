from typing import Callable, Dict, List, Type, Union

from openapi_core.casting.schemas.casters import (
    ArrayCaster, BaseSchemaCaster, CallableSchemaCaster, ComplexCaster,
    DummyCaster,
)
from openapi_core.casting.schemas.util import forcebool
from openapi_core.spec.paths import SpecPath


class SchemaCastersFactory:

    DUMMY_CASTERS: List[str] = [
        'string', 'object', 'any',
    ]
    PRIMITIVE_CASTERS: Dict[
        str, Callable[[str], Union[int, float, bool]]
    ] = {
        'integer': int,
        'number': float,
        'boolean': forcebool,
    }
    COMPLEX_CASTERS: Dict[str, Type[ComplexCaster]] = {
        'array': ArrayCaster,
    }

    def create(self, schema: SpecPath) -> BaseSchemaCaster:
        schema_type = schema.getkey('type', 'any')

        if schema_type in self.DUMMY_CASTERS:
            return DummyCaster(schema)

        if schema_type in self.PRIMITIVE_CASTERS:
            caster_callable = self.PRIMITIVE_CASTERS[schema_type]
            return CallableSchemaCaster(schema, caster_callable)

        return ArrayCaster(schema, self)
