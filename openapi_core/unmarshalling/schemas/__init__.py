from functools import partial

from isodate.isodatetime import parse_datetime
from openapi_schema_validator import OAS30ReadValidator
from openapi_schema_validator import OAS30WriteValidator
from openapi_schema_validator import OAS31Validator
from openapi_schema_validator._format import oas30_format_checker
from openapi_schema_validator._format import oas31_format_checker

from openapi_core.unmarshalling.schemas.enums import ValidationContext
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.util import format_byte
from openapi_core.unmarshalling.schemas.util import format_date
from openapi_core.unmarshalling.schemas.util import format_number
from openapi_core.unmarshalling.schemas.util import format_uuid

__all__ = [
    "oas30_format_unmarshallers",
    "oas31_format_unmarshallers",
    "oas30_request_schema_unmarshallers_factory",
    "oas30_response_schema_unmarshallers_factory",
    "oas31_request_schema_unmarshallers_factory",
    "oas31_response_schema_unmarshallers_factory",
    "oas31_schema_unmarshallers_factory",
]

oas30_format_unmarshallers = {
    # string compatible
    "date": format_date,
    "date-time": parse_datetime,
    "binary": bytes,
    "uuid": format_uuid,
    "byte": format_byte,
}
oas31_format_unmarshallers = oas30_format_unmarshallers

oas30_request_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS30WriteValidator,
    base_format_checker=oas30_format_checker,
    format_unmarshallers=oas30_format_unmarshallers,
    context=ValidationContext.REQUEST,
)

oas30_response_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS30ReadValidator,
    base_format_checker=oas30_format_checker,
    format_unmarshallers=oas30_format_unmarshallers,
    context=ValidationContext.RESPONSE,
)

oas31_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS31Validator,
    base_format_checker=oas31_format_checker,
    format_unmarshallers=oas31_format_unmarshallers,
)

# alias to v31 version (request/response are the same bcs no context needed)
oas31_request_schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
oas31_response_schema_unmarshallers_factory = (
    oas31_schema_unmarshallers_factory
)
