from openapi_core.schema.schemas.enums import SchemaType

from openapi_core.casting.schemas.casters import (
    PrimitiveCaster, DummyCaster, ArrayCaster
)
from openapi_core.casting.schemas.util import forcebool


class SchemaCastersFactory(object):

    DUMMY_CASTER = DummyCaster()
    PRIMITIVE_CASTERS = {
        SchemaType.STRING: DUMMY_CASTER,
        SchemaType.INTEGER: PrimitiveCaster(int),
        SchemaType.NUMBER: PrimitiveCaster(float),
        SchemaType.BOOLEAN: PrimitiveCaster(forcebool),
        SchemaType.OBJECT: DUMMY_CASTER,
        SchemaType.ANY: DUMMY_CASTER,
    }
    COMPLEX_CASTERS = {
        SchemaType.ARRAY: ArrayCaster,
    }

    def create(self, schema):
        if schema.type in self.PRIMITIVE_CASTERS:
            return self.PRIMITIVE_CASTERS[schema.type]
        elif schema.type in self.COMPLEX_CASTERS:
            caster_class = self.COMPLEX_CASTERS[schema.type]
            return caster_class(schema=schema, casters_factory=self)
