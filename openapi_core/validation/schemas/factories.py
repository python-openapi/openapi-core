from copy import deepcopy
from typing import Any
from typing import Optional
from typing import cast

from jsonschema._format import FormatChecker
from jsonschema.protocols import Validator
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.validators import SchemaValidator


class SchemaValidatorsFactory:
    def __init__(
        self,
        schema_validator_class: type[Validator],
        strict_schema_validator_class: Optional[type[Validator]] = None,
        format_checker: Optional[FormatChecker] = None,
    ):
        self.schema_validator_class = schema_validator_class
        self.strict_schema_validator_class = strict_schema_validator_class
        if format_checker is None:
            format_checker = self.schema_validator_class.FORMAT_CHECKER
        assert format_checker is not None
        self.format_checker = format_checker

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
        schema: SchemaPath,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
        strict_additional_properties: bool = False,
        require_all_properties: bool = False,
    ) -> SchemaValidator:
        validator_class: type[Validator] = self.schema_validator_class
        if strict_additional_properties:
            if self.strict_schema_validator_class is None:
                raise ValueError(
                    "Strict additional properties validation is not supported "
                    "by this factory."
                )
            validator_class = self.strict_schema_validator_class
        format_checker = self.get_format_checker(
            format_validators, extra_format_validators
        )
        with schema.resolve() as resolved:
            schema_value = resolved.contents
            if require_all_properties:
                schema_value = self._build_required_properties_schema(
                    schema_value
                )
            jsonschema_validator = validator_class(
                schema_value,
                _resolver=resolved.resolver,
                format_checker=format_checker,
            )

        return SchemaValidator(schema, jsonschema_validator)

    def _build_required_properties_schema(self, schema_value: Any) -> Any:
        updated = deepcopy(schema_value)
        self._set_required_properties(updated)
        return updated

    def _set_required_properties(self, schema: Any) -> None:
        if not isinstance(schema, dict):
            return

        properties = schema.get("properties")
        if isinstance(properties, dict) and properties:
            schema["required"] = [
                property_name
                for property_name, property_schema in properties.items()
                if not self._is_write_only_property(property_schema)
            ]
            for property_schema in properties.values():
                self._set_required_properties(property_schema)

        for keyword in (
            "allOf",
            "anyOf",
            "oneOf",
            "prefixItems",
        ):
            subschemas = schema.get(keyword)
            if isinstance(subschemas, list):
                for subschema in subschemas:
                    self._set_required_properties(subschema)

        for keyword in (
            "items",
            "contains",
            "if",
            "then",
            "else",
            "not",
            "propertyNames",
            "additionalProperties",
            "unevaluatedProperties",
            "unevaluatedItems",
            "contentSchema",
        ):
            self._set_required_properties(schema.get(keyword))

        for keyword in ("$defs", "definitions", "patternProperties"):
            subschemas_map = schema.get(keyword)
            if isinstance(subschemas_map, dict):
                for subschema in subschemas_map.values():
                    self._set_required_properties(subschema)

        dependent_schemas = schema.get("dependentSchemas")
        if isinstance(dependent_schemas, dict):
            for subschema in dependent_schemas.values():
                self._set_required_properties(subschema)

    def _is_write_only_property(self, property_schema: Any) -> bool:
        if not isinstance(property_schema, dict):
            return False
        return property_schema.get("writeOnly") is True
