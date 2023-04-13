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

__all__ = [
    "oas30_format_unmarshallers",
    "oas31_format_unmarshallers",
    "oas30_write_schema_unmarshallers_factory",
    "oas30_read_schema_unmarshallers_factory",
    "oas31_schema_unmarshallers_factory",
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
oas31_unmarshallers_dict = oas30_unmarshallers_dict.copy()
oas31_unmarshallers_dict.update(
    {
        "null": PrimitiveUnmarshaller,
    }
)

oas30_types_unmarshaller = TypesUnmarshaller(
    oas30_unmarshallers_dict,
    AnyUnmarshaller,
)
oas31_types_unmarshaller = TypesUnmarshaller(
    oas31_unmarshallers_dict,
    AnyUnmarshaller,
    multi=MultiTypeUnmarshaller,
)

oas30_format_unmarshallers = {
    # string compatible
    "date": format_date,
    "date-time": parse_datetime,
    "binary": bytes,
    "uuid": format_uuid,
    "byte": format_byte,
}
oas31_format_unmarshallers = oas30_format_unmarshallers

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

# alias to v31 version (request/response are the same bcs no context needed)
oas31_request_schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
oas31_response_schema_unmarshallers_factory = (
    oas31_schema_unmarshallers_factory
)
