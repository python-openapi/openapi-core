from collections import OrderedDict

from isodate.isodatetime import parse_datetime

from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.unmarshallers import AnyUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import ArrayUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import (
    MultiTypeUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import ObjectUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import (
    PrimitiveUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import TypesUnmarshaller
from openapi_core.unmarshalling.schemas.util import format_byte
from openapi_core.unmarshalling.schemas.util import format_date
from openapi_core.unmarshalling.schemas.util import format_uuid
from openapi_core.validation.schemas import (
    oas30_read_schema_validators_factory,
)
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas import oas31_schema_validators_factory
from openapi_core.validation.schemas import oas32_schema_validators_factory

__all__ = [
    "oas30_format_unmarshallers",
    "oas31_format_unmarshallers",
    "oas32_format_unmarshallers",
    "oas30_write_schema_unmarshallers_factory",
    "oas30_read_schema_unmarshallers_factory",
    "oas31_schema_unmarshallers_factory",
    "oas32_schema_unmarshallers_factory",
]

oas30_unmarshallers_dict = OrderedDict(
    [
        ("object", ObjectUnmarshaller),
        ("array", ArrayUnmarshaller),
        ("boolean", PrimitiveUnmarshaller),
        ("integer", PrimitiveUnmarshaller),
        ("number", PrimitiveUnmarshaller),
        ("string", PrimitiveUnmarshaller),
    ]
)
oas31_unmarshallers_dict = OrderedDict(
    [
        ("object", ObjectUnmarshaller),
        ("array", ArrayUnmarshaller),
        ("boolean", PrimitiveUnmarshaller),
        ("integer", PrimitiveUnmarshaller),
        ("number", PrimitiveUnmarshaller),
        ("string", PrimitiveUnmarshaller),
        ("null", PrimitiveUnmarshaller),
    ]
)

oas30_types_unmarshaller = TypesUnmarshaller(
    dict(oas30_unmarshallers_dict),
    AnyUnmarshaller,
)
oas31_types_unmarshaller = TypesUnmarshaller(
    dict(oas31_unmarshallers_dict),
    AnyUnmarshaller,
    multi=MultiTypeUnmarshaller,
)
oas32_types_unmarshaller = oas31_types_unmarshaller

oas30_format_unmarshallers = {
    # string compatible
    "date": format_date,
    "date-time": parse_datetime,
    "binary": bytes,
    "uuid": format_uuid,
    "byte": format_byte,
}
# NOTE: Intentionally reuse OAS 3.0 format unmarshallers for OAS 3.1/3.2
# to preserve backward compatibility for `byte`/`binary` formats.
# See https://github.com/python-openapi/openapi-core/issues/506
oas31_format_unmarshallers = oas30_format_unmarshallers
oas32_format_unmarshallers = oas31_format_unmarshallers

oas30_write_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    oas30_write_schema_validators_factory,
    oas30_types_unmarshaller,
    format_unmarshallers=oas30_format_unmarshallers,
)

oas30_read_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    oas30_read_schema_validators_factory,
    oas30_types_unmarshaller,
    format_unmarshallers=oas30_format_unmarshallers,
)

oas31_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    oas31_schema_validators_factory,
    oas31_types_unmarshaller,
    format_unmarshallers=oas31_format_unmarshallers,
)

oas32_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    oas32_schema_validators_factory,
    oas32_types_unmarshaller,
    format_unmarshallers=oas32_format_unmarshallers,
)

# alias to v31 version (request/response are the same bcs no context needed)
oas31_request_schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
oas31_response_schema_unmarshallers_factory = (
    oas31_schema_unmarshallers_factory
)

# alias to v32 version (request/response are the same bcs no context needed)
oas32_request_schema_unmarshallers_factory = oas32_schema_unmarshallers_factory
oas32_response_schema_unmarshallers_factory = (
    oas32_schema_unmarshallers_factory
)
