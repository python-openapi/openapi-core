from openapi_schema_validator import OAS30Validator

from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)

__all__ = [
    "oas30_request_schema_unmarshallers_factory",
    "oas30_response_schema_unmarshallers_factory",
]

oas30_request_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS30Validator,
    context=UnmarshalContext.REQUEST,
)

oas30_response_schema_unmarshallers_factory = SchemaUnmarshallersFactory(
    OAS30Validator,
    context=UnmarshalContext.RESPONSE,
)
