from collections import OrderedDict

from openapi_core.casting.schemas.casters import ArrayCaster
from openapi_core.casting.schemas.casters import BooleanCaster
from openapi_core.casting.schemas.casters import IntegerCaster
from openapi_core.casting.schemas.casters import NumberCaster
from openapi_core.casting.schemas.casters import ObjectCaster
from openapi_core.casting.schemas.casters import PrimitiveCaster
from openapi_core.casting.schemas.casters import TypesCaster
from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.validation.schemas import (
    oas30_read_schema_validators_factory,
)
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas import oas31_schema_validators_factory

__all__ = [
    "oas30_write_schema_casters_factory",
    "oas30_read_schema_casters_factory",
    "oas31_schema_casters_factory",
]

oas30_casters_dict = OrderedDict(
    [
        ("object", ObjectCaster),
        ("array", ArrayCaster),
        ("boolean", BooleanCaster),
        ("integer", IntegerCaster),
        ("number", NumberCaster),
        ("string", PrimitiveCaster),
    ]
)
oas31_casters_dict = oas30_casters_dict.copy()
oas31_casters_dict.update(
    {
        "null": PrimitiveCaster,
    }
)

oas30_types_caster = TypesCaster(
    oas30_casters_dict,
    PrimitiveCaster,
)
oas31_types_caster = TypesCaster(
    oas31_casters_dict,
    PrimitiveCaster,
    multi=PrimitiveCaster,
)

oas30_write_schema_casters_factory = SchemaCastersFactory(
    oas30_write_schema_validators_factory,
    oas30_types_caster,
)

oas30_read_schema_casters_factory = SchemaCastersFactory(
    oas30_read_schema_validators_factory,
    oas30_types_caster,
)

oas31_schema_casters_factory = SchemaCastersFactory(
    oas31_schema_validators_factory,
    oas31_types_caster,
)
