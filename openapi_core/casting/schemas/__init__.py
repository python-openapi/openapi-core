from collections import OrderedDict

from openapi_core.casting.schemas.casters import AnyCaster
from openapi_core.casting.schemas.casters import ArrayCaster
from openapi_core.casting.schemas.casters import BooleanCaster
from openapi_core.casting.schemas.casters import IntegerCaster
from openapi_core.casting.schemas.casters import MultiTypeCaster
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
from openapi_core.validation.schemas import oas32_schema_validators_factory

__all__ = [
    "oas30_write_schema_casters_factory",
    "oas30_read_schema_casters_factory",
    "oas31_schema_casters_factory",
    "oas32_schema_casters_factory",
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
    AnyCaster,
)
# OAS 3.1/3.2: ``type`` may be a list. ``multi=MultiTypeCaster`` enables the
# real coercion path. ``multi`` is intentionally left ``None`` for OAS 3.0 so
# any ``type: [..]`` in a 3.0 spec still raises
# ``TypeError("caster does not accept multiple types")`` at dispatch time.
oas31_types_caster = TypesCaster(
    oas31_casters_dict,
    AnyCaster,
    multi=MultiTypeCaster,
)
oas32_types_caster = oas31_types_caster

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
oas32_schema_casters_factory = SchemaCastersFactory(
    oas32_schema_validators_factory,
    oas32_types_caster,
)
