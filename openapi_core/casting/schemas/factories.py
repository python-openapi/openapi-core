from typing import Dict

from openapi_core.casting.schemas.casters import ArrayCaster
from openapi_core.casting.schemas.casters import BaseSchemaCaster
from openapi_core.casting.schemas.casters import CallableSchemaCaster
from openapi_core.casting.schemas.casters import DummyCaster
from openapi_core.casting.schemas.datatypes import CasterCallable
from openapi_core.spec import Spec
from openapi_core.util import forcebool


class SchemaCastersFactory:
    DUMMY_CASTERS = [
        "string",
        "object",
        "any",
    ]
    PRIMITIVE_CASTERS: Dict[str, CasterCallable] = {
        "integer": int,
        "number": float,
        "boolean": forcebool,
    }
    COMPLEX_CASTERS = {
        "array": ArrayCaster,
    }

    def create(self, schema: Spec) -> BaseSchemaCaster:
        schema_type = schema.getkey("type", "any")

        if schema_type in self.DUMMY_CASTERS:
            return DummyCaster(schema)

        if schema_type in self.PRIMITIVE_CASTERS:
            caster_callable = self.PRIMITIVE_CASTERS[schema_type]
            return CallableSchemaCaster(schema, caster_callable)

        return ArrayCaster(schema, self)
