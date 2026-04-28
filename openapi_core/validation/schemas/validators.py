import logging
from functools import cached_property
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Optional

from jsonschema.exceptions import FormatError
from jsonschema.protocols import Validator
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas.datatypes import FormatValidator
from openapi_core.validation.schemas.datatypes import ValidationState
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.exceptions import ValidateError

if TYPE_CHECKING:
    from openapi_core.casting.schemas.casters import SchemaCaster

log = logging.getLogger(__name__)


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
        errors_iter = self.validator.iter_errors(value)
        errors = tuple(errors_iter)
        if errors:
            schema_type = (self.schema / "type").read_str_or_list("any")
            raise InvalidSchemaValue(value, schema_type, schema_errors=errors)

    def validate_state(self, value: Any) -> ValidationState:
        self.validate(value)
        return self._build_trusted_state(value)

    def _build_trusted_state(self, value: Any) -> ValidationState:
        primitive_type = self.get_primitive_type(value)
        property_states = {}
        additional_property_states = {}
        item_states: tuple[ValidationState, ...] = ()
        one_of_state = None
        any_of_states: tuple[ValidationState, ...] = ()
        all_of_states: tuple[ValidationState, ...] = ()

        if "oneOf" in self.schema:
            one_of_schema = self.get_one_of_schema(value)
            if one_of_schema is not None:
                one_of_state = self.evolve(one_of_schema)._build_trusted_state(
                    value
                )

        if "anyOf" in self.schema:
            any_of_schemas = tuple(self.iter_any_of_schemas(value))
            if any_of_schemas:
                any_of_states = tuple(
                    self.evolve(any_of_schema)._build_trusted_state(value)
                    for any_of_schema in any_of_schemas
                )

        if "allOf" in self.schema:
            all_of_schemas = tuple(self.iter_all_of_schemas(value))
            if all_of_schemas:
                all_of_states = tuple(
                    self.evolve(all_of_schema)._build_trusted_state(value)
                    for all_of_schema in all_of_schemas
                )

        if primitive_type == "object" and isinstance(value, dict):
            for prop_name, prop_schema in self._get_input_properties(
                value
            ).items():
                property_states[prop_name] = self.evolve(
                    prop_schema
                )._build_trusted_state(value[prop_name])
            for (
                prop_name,
                additional_prop_schema,
            ) in self._get_input_additional_properties(value).items():
                additional_property_states[prop_name] = self.evolve(
                    additional_prop_schema
                )._build_trusted_state(value[prop_name])
        elif primitive_type == "array" and isinstance(value, list):
            item_states = tuple(self.iter_item_states(value))

        return ValidationState(
            self.schema,
            value,
            primitive_type=primitive_type,
            property_states=property_states,
            additional_property_states=additional_property_states,
            item_states=item_states,
            one_of_state=one_of_state,
            any_of_states=any_of_states,
            all_of_states=all_of_states,
        )

    def evolve(self, schema: SchemaPath) -> "SchemaValidator":
        cls = self.__class__

        with schema.resolve() as resolved:
            validator = self.validator.evolve(
                schema=resolved.contents, _resolver=resolved.resolver
            )
            return cls(schema, validator)

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

    def iter_item_states(self, value: list[Any]) -> Iterator[ValidationState]:
        if "items" not in self.schema:
            any_schema = SchemaPath.from_dict({})
            any_validator = self.evolve(any_schema)
            for item in value:
                yield any_validator._build_trusted_state(item)
            return

        items_schema = self.schema / "items"
        item_validator = self.evolve(items_schema)
        for item in value:
            yield item_validator._build_trusted_state(item)

    def _get_input_properties(
        self, value: dict[str, Any]
    ) -> dict[str, SchemaPath]:
        if "properties" not in self.schema:
            return {}

        properties: dict[str, SchemaPath] = {}
        for prop_name, prop_schema in (self.schema / "properties").items():
            if not isinstance(prop_name, str):
                continue
            if prop_name not in value:
                continue
            properties[prop_name] = prop_schema

        return properties

    def _get_input_additional_properties(
        self, value: dict[str, Any]
    ) -> dict[str, SchemaPath]:
        additional_properties = self.schema.get("additionalProperties", True)
        if additional_properties is False:
            return {}

        property_names = set(self._get_input_properties(value))
        if additional_properties is True:
            additional_prop_schema = SchemaPath.from_dict({"nullable": True})
        else:
            additional_prop_schema = self.schema / "additionalProperties"

        return {
            prop_name: additional_prop_schema
            for prop_name in value
            if prop_name not in property_names
        }

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

        one_of_schemas = self.schema / "oneOf"
        for subschema in one_of_schemas:
            validator = self.evolve(subschema)
            try:
                test_value = value
                # Only cast if caster provided (opt-in behavior)
                if caster is not None:
                    try:
                        # Convert to dict if it's not exactly a plain dict
                        # (e.g., ImmutableMultiDict from werkzeug)
                        if type(value) is not dict:
                            test_value = dict(value)
                        else:
                            test_value = value
                        test_value = caster.evolve(subschema).cast(test_value)
                    except (ValueError, TypeError, Exception):
                        # If casting fails, try validation with original value
                        # We catch generic Exception to handle CastError without circular import
                        test_value = value

                validator.validate(test_value)
            except ValidateError:
                continue
            else:
                return subschema

        log.warning("valid oneOf schema not found")
        return None

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

        any_of_schemas = self.schema / "anyOf"
        for subschema in any_of_schemas:
            validator = self.evolve(subschema)
            try:
                test_value = value
                # Only cast if caster provided (opt-in behavior)
                if caster is not None:
                    try:
                        # Convert to dict if it's not exactly a plain dict
                        if type(value) is not dict:
                            test_value = dict(value)
                        else:
                            test_value = value
                        test_value = caster.evolve(subschema).cast(test_value)
                    except (ValueError, TypeError, Exception):
                        # If casting fails, try validation with original value
                        # We catch generic Exception to handle CastError without circular import
                        test_value = value

                validator.validate(test_value)
            except ValidateError:
                continue
            else:
                yield subschema

    def iter_all_of_schemas(
        self,
        value: Any,
    ) -> Iterator[SchemaPath]:
        if "allOf" not in self.schema:
            return

        all_of_schemas = self.schema / "allOf"
        for subschema in all_of_schemas:
            if "type" not in subschema:
                continue
            validator = self.evolve(subschema)
            try:
                validator.validate(value)
            except ValidateError:
                log.warning("invalid allOf schema found")
            else:
                yield subschema
