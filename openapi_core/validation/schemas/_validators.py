from typing import Any
from typing import Callable
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import cast

from jsonschema._utils import extras_msg
from jsonschema._utils import find_additional_properties
from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator
from jsonschema.validators import extend

from openapi_core.schema.binary import is_binary_schema

_KeywordValidator = Callable[[Any, Any, Any, Mapping[str, Any]], Iterator[Any]]


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


def build_binary_aware_validator(
    validator_class: type[Validator],
) -> type[Validator]:
    """Extend ``validator_class`` so raw ``bytes`` validate against
    "binary" string schemas.

    OpenAPI lets a ``bytes`` payload flow through a ``type: string``
    schema whose ``format``/``contentMediaType`` marks it as opaque
    binary (file uploads, ``application/octet-stream`` bodies). Plain
    jsonschema rejects ``bytes`` as a non-``string`` and then crashes or
    misfires on ``pattern``/length/``enum``/``format`` keywords.

    We treat the byte payload as *opaque* -- consistent with JSON Schema
    2020-12 where ``contentMediaType``/``contentEncoding`` are
    annotations, not assertions. The ``type`` keyword accepts the bytes,
    and the string-only assertion keywords are skipped *only* at a
    binary node holding bytes. Every other instance/keyword combination
    is delegated unchanged to the wrapped validator, so behaviour for
    ordinary strings (including the invariant that ``bytes`` is still
    rejected against a plain ``type: string``) is preserved. Because the
    binary branch now validates, jsonschema's own ``oneOf``/``anyOf``/
    ``allOf`` selection picks it without any parallel value walk.
    """
    type_validator = validator_class.VALIDATORS.get("type")

    def _is_opaque_binary(instance: Any, schema: Mapping[str, Any]) -> bool:
        return isinstance(instance, bytes) and is_binary_schema(schema)

    def binary_aware_type(
        validator: Any,
        data_type: Any,
        instance: Any,
        schema: Mapping[str, Any],
    ) -> Iterator[Any]:
        if _is_opaque_binary(instance, schema):
            return
        if type_validator is not None:
            yield from type_validator(validator, data_type, instance, schema)

    def _skip_binary(
        original: Optional[_KeywordValidator],
    ) -> _KeywordValidator:
        def keyword(
            validator: Any,
            keyword_value: Any,
            instance: Any,
            schema: Mapping[str, Any],
        ) -> Iterator[Any]:
            if _is_opaque_binary(instance, schema):
                return
            if original is not None:
                yield from original(validator, keyword_value, instance, schema)

        return keyword

    validators: dict[str, _KeywordValidator] = {"type": binary_aware_type}
    # String-only assertion keywords: harmless to skip on an opaque byte
    # payload, and ``pattern`` in particular raises ``TypeError`` when
    # applied to ``bytes``.
    for keyword_name in (
        "pattern",
        "minLength",
        "maxLength",
        "enum",
        "format",
    ):
        validators[keyword_name] = _skip_binary(
            validator_class.VALIDATORS.get(keyword_name)
        )

    return cast(
        type[Validator],
        extend(validator_class, validators=validators),
    )


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
