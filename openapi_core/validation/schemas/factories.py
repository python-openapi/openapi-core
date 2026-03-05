from copy import deepcopy
from functools import lru_cache
from typing import Any
from typing import Optional
from typing import cast

from jsonschema._format import FormatChecker
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas._validators import (
    build_enforce_properties_required_validator,
)
from openapi_core.validation.schemas._validators import (
    build_forbid_unspecified_additional_properties_validator,
)
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.validators import SchemaValidator


class SchemaValidatorsFactory:
    def __init__(
        self,
        schema_validator_cls: type[Validator],
        format_checker: Optional[FormatChecker] = None,
    ):
        self.schema_validator_cls = schema_validator_cls
        if format_checker is None:
            format_checker = self.schema_validator_cls.FORMAT_CHECKER
        assert format_checker is not None
        self.format_checker = format_checker

    def get_validator_cls(
        self, spec: SchemaPath, schema: SchemaPath
    ) -> type[Validator]:
        return self.schema_validator_cls

    def get_format_checker(
        self,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
    ) -> FormatChecker:
        format_checker: FormatChecker
        if format_validators is None:
            format_checker = deepcopy(cast(FormatChecker, self.format_checker))
        else:
            format_checker = FormatChecker([])
            format_checker = self._add_validators(
                cast(FormatChecker, format_checker), format_validators
            )
        format_checker = self._add_validators(
            cast(FormatChecker, format_checker), extra_format_validators
        )
        return format_checker

    def _add_validators(
        self,
        base_format_checker: FormatChecker,
        format_validators: Optional[FormatValidatorsDict] = None,
    ) -> FormatChecker:
        if format_validators is not None:
            for name, check in format_validators.items():
                base_format_checker.checks(name)(check)
        return base_format_checker

    def create(
        self,
        spec: SchemaPath,
        schema: SchemaPath,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
        forbid_unspecified_additional_properties: bool = False,
        enforce_properties_required: bool = False,
    ) -> SchemaValidator:
        validator_cls: type[Validator] = self.get_validator_cls(spec, schema)
        if enforce_properties_required:
            validator_cls = build_enforce_properties_required_validator(
                validator_cls
            )
        if forbid_unspecified_additional_properties:
            validator_cls = (
                build_forbid_unspecified_additional_properties_validator(
                    validator_cls
                )
            )

        format_checker = self.get_format_checker(
            format_validators, extra_format_validators
        )
        with schema.resolve() as resolved:
            jsonschema_validator = validator_cls(
                resolved.contents,
                _resolver=resolved.resolver,
                format_checker=format_checker,
            )

        return SchemaValidator(schema, jsonschema_validator)


class DialectSchemaValidatorsFactory(SchemaValidatorsFactory):
    def __init__(
        self,
        schema_validator_cls: type[Validator],
        default_jsonschema_dialect_id: str,
        format_checker: Optional[FormatChecker] = None,
    ):
        super().__init__(schema_validator_cls, format_checker)
        self.default_jsonschema_dialect_id = default_jsonschema_dialect_id

    def get_validator_cls(
        self, spec: SchemaPath, schema: SchemaPath
    ) -> type[Validator]:
        dialect_id = self._get_dialect_id(spec, schema)

        validator_cls = self._get_validator_class_for_dialect(dialect_id)
        if validator_cls is None:
            raise ValueError(f"Unknown JSON Schema dialect: {dialect_id!r}")

        return validator_cls

    def _get_dialect_id(
        self,
        spec: SchemaPath,
        schema: SchemaPath,
    ) -> str:
        try:
            return (schema / "$schema").read_str()
        except KeyError:
            return self._get_default_jsonschema_dialect_id(spec)

    def _get_default_jsonschema_dialect_id(self, spec: SchemaPath) -> str:
        return (spec / "jsonSchemaDialect").read_str(
            default=self.default_jsonschema_dialect_id
        )

    @lru_cache
    def _get_validator_class_for_dialect(
        self, dialect_id: str
    ) -> type[Validator] | None:
        return cast(
            type[Validator] | None,
            validator_for(
                {"$schema": dialect_id},
                default=cast(Any, None),
            ),
        )
