from typing import Any
from typing import Iterator
from typing import Mapping
from typing import cast

from jsonschema._utils import extras_msg
from jsonschema._utils import find_additional_properties
from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator
from jsonschema.validators import extend


def build_forbid_unspecified_additional_properties_validator(
    validator_class: type[Validator],
) -> type[Validator]:
    properties_validator = validator_class.VALIDATORS.get("properties")
    type_validator = validator_class.VALIDATORS.get("type")

    def strict_properties(
        validator: Any,
        properties: Any,
        instance: Any,
        schema: Mapping[str, Any],
    ) -> Iterator[Any]:
        if properties_validator is not None:
            yield from properties_validator(
                validator, properties, instance, schema
            )
        yield from iter_missing_additional_properties_errors(
            validator, instance, schema
        )

    def strict_type(
        validator: Any,
        data_type: Any,
        instance: Any,
        schema: Mapping[str, Any],
    ) -> Iterator[Any]:
        if type_validator is not None:
            yield from type_validator(validator, data_type, instance, schema)

        schema_types = data_type
        if isinstance(schema_types, str):
            schema_types = [schema_types]
        if not isinstance(schema_types, list):
            return
        if "object" not in schema_types:
            return
        if "additionalProperties" in schema or "properties" in schema:
            return

        yield from iter_missing_additional_properties_errors(
            validator, instance, schema
        )

    return cast(
        type[Validator],
        extend(
            validator_class,
            validators={
                "properties": strict_properties,
                "type": strict_type,
            },
        ),
    )


def iter_missing_additional_properties_errors(
    validator: Any,
    instance: Any,
    schema: Mapping[str, Any],
) -> Iterator[ValidationError]:
    if not validator.is_type(instance, "object"):
        return

    if "additionalProperties" in schema:
        return

    extras = sorted(set(find_additional_properties(instance, schema)))

    if extras:
        error = "Additional properties are not allowed (%s %s unexpected)"
        yield ValidationError(error % extras_msg(extras))


def build_enforce_properties_required_validator(
    validator_class: type[Validator],
) -> type[Validator]:
    properties_validator = validator_class.VALIDATORS.get("properties")

    def enforce_properties(
        validator: Any,
        properties: Any,
        instance: Any,
        schema: Mapping[str, Any],
    ) -> Iterator[Any]:
        if properties_validator is not None:
            yield from properties_validator(
                validator, properties, instance, schema
            )

        if not validator.is_type(instance, "object"):
            return

        for prop_name, prop_schema in properties.items():
            if prop_name not in instance:
                if (
                    isinstance(prop_schema, dict)
                    and prop_schema.get("writeOnly") is True
                ):
                    continue
                yield ValidationError(f"'{prop_name}' is a required property")

    return cast(
        type[Validator],
        extend(
            validator_class,
            validators={
                "properties": enforce_properties,
            },
        ),
    )
