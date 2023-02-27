from openapi_schema_validator import OAS30ReadValidator
from openapi_schema_validator import OAS30WriteValidator
from openapi_schema_validator import OAS31Validator

from openapi_core.validation.schemas.factories import SchemaValidatorsFactory

__all__ = [
    "oas30_write_schema_validators_factory",
    "oas30_read_schema_validators_factory",
    "oas31_schema_validators_factory",
]

oas30_write_schema_validators_factory = SchemaValidatorsFactory(
    OAS30WriteValidator,
)

oas30_read_schema_validators_factory = SchemaValidatorsFactory(
    OAS30ReadValidator,
)

oas31_schema_validators_factory = SchemaValidatorsFactory(
    OAS31Validator,
    # FIXME: OpenAPI 3.1 schema validator uses OpenAPI 3.0 format checker.
    # See https://github.com/python-openapi/openapi-core/issues/506
    format_checker=OAS30ReadValidator.FORMAT_CHECKER,
)
