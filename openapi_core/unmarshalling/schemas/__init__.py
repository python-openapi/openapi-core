from openapi_schema_validator import OAS30Validator
from openapi_schema_validator import OAS31Validator

from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)

__all__ = [
    "oas30_request_schema_unmarshallers_factory",
    "oas30_response_schema_unmarshallers_factory",
    "oas31_request_schema_unmarshallers_factory",
    "oas31_response_schema_unmarshallers_factory",
    "oas31_schema_unmarshallers_factory",
]

oas30_request_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS30Validator,
    context=UnmarshalContext.REQUEST,
)

oas30_response_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS30Validator,
    context=UnmarshalContext.RESPONSE,
)

oas31_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS31Validator,
)

# alias to v31 version (request/response are the same bcs no context needed)
oas31_request_schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
oas31_response_schema_unmarshallers_factory = (
    oas31_schema_unmarshallers_factory
)
