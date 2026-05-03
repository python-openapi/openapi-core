import logging
from copy import deepcopy
from functools import cached_property
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Optional
from typing import Union
from typing import cast

from jsonschema.exceptions import FormatError
from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas.datatypes import FormatValidator
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.exceptions import ValidateError

if TYPE_CHECKING:
    from openapi_core.casting.schemas.casters import SchemaCaster

log = logging.getLogger(__name__)


_MISSING = object()


class SchemaValidator:
    def __init__(
        self,
        schema: SchemaPath,
        validator: Validator,
    ):
        self.schema = schema
        self.validator = validator

    def __contains__(self, schema_format: str) -> bool:
        return schema_format in self.validator.format_checker.checkers

    def validate(self, value: Any) -> None:
        validation_value = self.get_binary_validation_value(value)
        errors = tuple(
            self.iter_errors(
                value,
                validation_value=validation_value,
            )
        )
        if errors:
            schema_type = (self.schema / "type").read_str_or_list("any")
            raise InvalidSchemaValue(value, schema_type, schema_errors=errors)

    def iter_errors(
        self,
        value: Any,
        validation_value: Any = _MISSING,
    ) -> Iterator[Exception]:
        if validation_value is _MISSING:
            validation_value = self.get_binary_validation_value(value)

        yield from self.base_validator.iter_errors(validation_value)
        yield from self.iter_composed_schema_errors(value)

    def evolve(self, schema: SchemaPath) -> "SchemaValidator":
        cls = self.__class__

        with schema.resolve() as resolved:
            validator = self.validator.evolve(
                schema=resolved.contents, _resolver=resolved.resolver
            )
            return cls(schema, validator)

    @cached_property
    def base_validator(self) -> Validator:
        with self.schema.resolve() as resolved:
            schema = cast(dict[str, Any], deepcopy(resolved.contents))

        for keyword in ["oneOf", "anyOf", "allOf"]:
            schema.pop(keyword, None)

        return self.validator.evolve(schema=schema)

    def type_validator(
        self, value: Any, type_override: Optional[str] = None
    ) -> bool:
        callable = self.get_type_validator_callable(
            type_override=type_override
        )
        return callable(value)

    def format_validator(self, value: Any) -> bool:
        try:
            self.format_validator_callable(value)
        except FormatError:
            return False
        else:
            return True

    def get_type_validator_callable(
        self, type_override: Optional[str] = None
    ) -> FormatValidator:
        schema_type = type_override or (self.schema / "type").read_str(None)
        if schema_type in self.validator.TYPE_CHECKER._type_checkers:
            return partial(
                self.validator.TYPE_CHECKER.is_type, type=schema_type
            )

        return lambda x: True

    @cached_property
    def format_validator_callable(self) -> FormatValidator:
        schema_format = (self.schema / "format").read_str(None)
        if schema_format in self.validator.format_checker.checkers:
            return partial(
                self.validator.format_checker.check, format=schema_format
            )

        return lambda x: True

    def get_primitive_type(self, value: Any) -> Optional[str]:
        schema_types = (self.schema / "type").read_str_or_list(None)
        if isinstance(schema_types, str):
            return schema_types
        if schema_types is None:
            schema_types = sorted(self.validator.TYPE_CHECKER._type_checkers)
        assert isinstance(schema_types, list)
        for schema_type in schema_types:
            if self.accepts_binary_string_value(schema_type, value):
                return schema_type
            result = self.type_validator(value, type_override=schema_type)
            if not result:
                continue
            result = self.format_validator(value)
            if not result:
                continue
            assert isinstance(schema_type, (str, type(None)))
            return schema_type
        # OpenAPI 3.0: None is not a primitive type so None value will not find any type
        return None

    def accepts_binary_string_value(
        self,
        schema_type: Optional[Union[str, list[str]]],
        value: Any,
    ) -> bool:
        if not isinstance(value, bytes):
            return False

        if isinstance(schema_type, list):
            if "string" not in schema_type:
                return False
        elif schema_type != "string":
            return False

        schema_format = (self.schema / "format").read_str(None)
        return schema_format in ("binary", "byte")

    def get_binary_validation_value(self, value: Any) -> Any:
        # OpenAPI binary and byte string values are represented as bytes,
        # but jsonschema validates string schemas against text values.
        if self.accepts_binary_string_value(
            (self.schema / "type").read_str_or_list(None), value
        ):
            return self.decode_binary_string_value(value)

        normalized = value

        if isinstance(normalized, dict):
            return self.get_binary_validation_mapping_value(normalized)

        if isinstance(normalized, list) and "items" in self.schema:
            return self.get_binary_validation_array_value(normalized)

        return normalized

    def iter_composed_schema_errors(
        self, value: Any
    ) -> Iterator[ValidationError]:
        if "oneOf" in self.schema:
            matched_schemas = list(
                self.iter_matching_composed_schemas("oneOf", value)
            )
            if len(matched_schemas) != 1:
                if not matched_schemas:
                    message = f"{value!r} is not valid under any of the given schemas"
                else:
                    message = (
                        f"{value!r} is valid under each of {matched_schemas!r}"
                    )
                yield ValidationError(message)

        if "anyOf" in self.schema:
            matched_schemas = list(
                self.iter_matching_composed_schemas("anyOf", value)
            )
            if not matched_schemas:
                yield ValidationError(
                    f"{value!r} is not valid under any of the given schemas"
                )

        if "allOf" in self.schema:
            invalid_schemas = list(self.iter_invalid_all_of_schemas(value))
            for _ in invalid_schemas:
                yield ValidationError(
                    f"{value!r} is not valid under all of the given schemas"
                )

    def decode_binary_string_value(self, value: bytes) -> str:
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("ASCII", errors="surrogateescape")

    def get_binary_validation_mapping_value(self, value: Any) -> Any:
        normalized = value

        if "properties" in self.schema:
            for prop_name, prop_schema in (self.schema / "properties").items():
                if prop_name not in value:
                    continue
                prop_value = self.evolve(
                    prop_schema
                ).get_binary_validation_value(value[prop_name])
                if prop_value is value[prop_name]:
                    continue
                if normalized is value:
                    normalized = dict(value)
                normalized[prop_name] = prop_value

        additional_properties = self.schema.get("additionalProperties", True)
        if additional_properties in (True, False):
            return normalized

        property_names = set()
        if "properties" in self.schema:
            property_names = set((self.schema / "properties").keys())
        additional_validator = self.evolve(
            self.schema / "additionalProperties"
        )
        for prop_name, prop_value in value.items():
            if prop_name in property_names:
                continue
            normalized_prop_value = (
                additional_validator.get_binary_validation_value(prop_value)
            )
            if normalized_prop_value is prop_value:
                continue
            if normalized is value:
                normalized = dict(value)
            normalized[prop_name] = normalized_prop_value

        return normalized

    def get_binary_validation_array_value(self, value: Any) -> Any:
        item_validator = self.evolve(self.schema / "items")
        normalized = None

        for idx, item in enumerate(value):
            normalized_item = item_validator.get_binary_validation_value(item)
            if normalized_item is item:
                continue
            if normalized is None:
                normalized = list(value)
            normalized[idx] = normalized_item

        if normalized is None:
            return value

        return normalized

    def iter_valid_schemas(self, value: Any) -> Iterator[SchemaPath]:
        yield self.schema

        one_of_schema = self.get_one_of_schema(value)
        if one_of_schema is not None:
            yield one_of_schema

        yield from self.iter_any_of_schemas(value)
        yield from self.iter_all_of_schemas(value)

    def get_one_of_schema(
        self,
        value: Any,
        caster: Optional["SchemaCaster"] = None,
    ) -> Optional[SchemaPath]:
        """Find the matching oneOf schema.

        Args:
            value: The value to match against schemas
            caster: Optional caster for type coercion during matching.
                    Useful for form-encoded data where types need casting.
        """
        if "oneOf" not in self.schema:
            return None

        matched_schemas = list(
            self.iter_matching_composed_schemas(
                "oneOf",
                value,
                caster=caster,
            )
        )
        if len(matched_schemas) == 1:
            return matched_schemas[0]

        log.warning("valid oneOf schema not found")
        return None

    def iter_matching_composed_schemas(
        self,
        keyword: str,
        value: Any,
        caster: Optional["SchemaCaster"] = None,
    ) -> Iterator[SchemaPath]:
        if keyword not in self.schema:
            return

        for subschema in self.schema / keyword:
            validator = self.evolve(subschema)
            try:
                test_value = value
                if caster is not None:
                    try:
                        if type(value) is not dict:
                            test_value = dict(value)
                        else:
                            test_value = value
                        test_value = caster.evolve(subschema).cast(test_value)
                    except (ValueError, TypeError, Exception):
                        test_value = value

                validator.validate(test_value)
            except ValidateError:
                continue
            else:
                yield subschema

    def iter_any_of_schemas(
        self,
        value: Any,
        caster: Optional["SchemaCaster"] = None,
    ) -> Iterator[SchemaPath]:
        """Iterate matching anyOf schemas.

        Args:
            value: The value to match against schemas
            caster: Optional caster for type coercion during matching.
                    Useful for form-encoded data where types need casting.
        """
        if "anyOf" not in self.schema:
            return

        yield from self.iter_matching_composed_schemas(
            "anyOf",
            value,
            caster=caster,
        )

    def iter_all_of_schemas(
        self,
        value: Any,
    ) -> Iterator[SchemaPath]:
        if "allOf" not in self.schema:
            return

        for subschema in self.schema / "allOf":
            validator = self.evolve(subschema)
            try:
                validator.validate(value)
            except ValidateError:
                log.warning("invalid allOf schema found")
            else:
                yield subschema

    def iter_invalid_all_of_schemas(self, value: Any) -> Iterator[SchemaPath]:
        if "allOf" not in self.schema:
            return

        for subschema in self.schema / "allOf":
            validator = self.evolve(subschema)
            try:
                validator.validate(value)
            except ValidateError:
                yield subschema
