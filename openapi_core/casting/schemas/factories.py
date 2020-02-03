from openapi_core.schema.schemas.enums import SchemaType

from openapi_core.casting.schemas.casters import (
    PrimitiveCaster, DummyCaster, ArrayCaster
)
from openapi_core.casting.schemas.util import forcebool


class SchemaCastersFactory(object):

    DUMMY_CASTERS = [
        SchemaType.STRING, SchemaType.OBJECT, SchemaType.ANY,
    ]
    PRIMITIVE_CASTERS = {
        SchemaType.INTEGER: int,
        SchemaType.NUMBER: float,
        SchemaType.BOOLEAN: forcebool,
    }
    COMPLEX_CASTERS = {
        SchemaType.ARRAY: ArrayCaster,
    }

    def create(self, schema):
        if schema.type in self.DUMMY_CASTERS:
            return DummyCaster()
        elif schema.type in self.PRIMITIVE_CASTERS:
            caster_callable = self.PRIMITIVE_CASTERS[schema.type]
            return PrimitiveCaster(schema, caster_callable)
        elif schema.type in self.COMPLEX_CASTERS:
            caster_class = self.COMPLEX_CASTERS[schema.type]
            return caster_class(schema, self)
