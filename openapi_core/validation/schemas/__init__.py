from functools import partial

from lazy_object_proxy import Proxy
from openapi_schema_validator import OAS30ReadValidator
from openapi_schema_validator import OAS30WriteValidator
from openapi_schema_validator import OAS31Validator
from openapi_schema_validator import OAS32Validator

from openapi_core.validation.schemas._validators import (
    build_strict_additional_properties_validator,
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
    Proxy(
        partial(
            build_strict_additional_properties_validator, OAS30WriteValidator
        )
    ),
)

oas30_read_schema_validators_factory = SchemaValidatorsFactory(
    OAS30ReadValidator,
    Proxy(
        partial(
            build_strict_additional_properties_validator, OAS30ReadValidator
        )
    ),
)

oas31_schema_validators_factory = SchemaValidatorsFactory(
    OAS31Validator,
    Proxy(
        partial(build_strict_additional_properties_validator, OAS31Validator)
    ),
    # FIXME: OpenAPI 3.1 schema validator uses OpenAPI 3.0 format checker.
    # See https://github.com/python-openapi/openapi-core/issues/506
    format_checker=OAS30ReadValidator.FORMAT_CHECKER,
)

oas32_schema_validators_factory = SchemaValidatorsFactory(
    OAS32Validator,
    Proxy(
        partial(build_strict_additional_properties_validator, OAS32Validator)
    ),
)
