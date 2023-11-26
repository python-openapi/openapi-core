from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.casting.schemas.casters import SchemaCaster
from openapi_core.casting.schemas.casters import TypesCaster
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory


class SchemaCastersFactory:
    def __init__(
        self,
        schema_validators_factory: SchemaValidatorsFactory,
        types_caster: TypesCaster,
    ):
        self.schema_validators_factory = schema_validators_factory
        self.types_caster = types_caster

    def create(
        self,
        schema: SchemaPath,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
    ) -> SchemaCaster:
        schema_validator = self.schema_validators_factory.create(
            schema,
            format_validators=format_validators,
            extra_format_validators=extra_format_validators,
        )

        return SchemaCaster(schema, schema_validator, self.types_caster)
