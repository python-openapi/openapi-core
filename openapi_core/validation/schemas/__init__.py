from openapi_schema_validator import OAS31_BASE_DIALECT_ID
from openapi_schema_validator import OAS32_BASE_DIALECT_ID
from openapi_schema_validator import OAS30ReadValidator
from openapi_schema_validator import OAS30WriteValidator
from openapi_schema_validator import OAS31Validator
from openapi_schema_validator import OAS32Validator

from openapi_core.validation.schemas.factories import (
    DialectSchemaValidatorsFactory,
)
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory

__all__ = [
    "oas30_write_schema_validators_factory",
    "oas30_read_schema_validators_factory",
    "oas31_schema_validators_factory",
    "oas32_schema_validators_factory",
]

oas30_write_schema_validators_factory = SchemaValidatorsFactory(
    OAS30WriteValidator,
)

oas30_read_schema_validators_factory = SchemaValidatorsFactory(
    OAS30ReadValidator,
)

oas31_schema_validators_factory = DialectSchemaValidatorsFactory(
    OAS31Validator,
    OAS31_BASE_DIALECT_ID,
    # NOTE: Intentionally use OAS 3.0 format checker for OAS 3.1 to preserve
    # backward compatibility for `byte`/`binary` formats.
    # See https://github.com/python-openapi/openapi-core/issues/506
    format_checker=OAS30ReadValidator.FORMAT_CHECKER,
)

oas32_schema_validators_factory = DialectSchemaValidatorsFactory(
    OAS32Validator,
    OAS32_BASE_DIALECT_ID,
)
