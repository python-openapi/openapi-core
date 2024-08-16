import logging
from functools import cached_property
from functools import partial
from typing import Any
from typing import Iterator
from typing import Optional

from jsonschema.exceptions import FormatError
from jsonschema.protocols import Validator
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas.datatypes import FormatValidator
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.exceptions import ValidateError

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
            schema_type = self.schema.getkey("type", "any")
            raise InvalidSchemaValue(value, schema_type, schema_errors=errors)

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
        schema_type = type_override or self.schema.getkey("type")
        if schema_type in self.validator.TYPE_CHECKER._type_checkers:
            return partial(
                self.validator.TYPE_CHECKER.is_type, type=schema_type
            )

        return lambda x: True

    @cached_property
    def format_validator_callable(self) -> FormatValidator:
        schema_format = self.schema.getkey("format")
        if schema_format in self.validator.format_checker.checkers:
            return partial(
                self.validator.format_checker.check, format=schema_format
            )

        return lambda x: True

    def get_primitive_type(self, value: Any) -> Optional[str]:
        schema_types = self.schema.getkey("type")
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
    ) -> Optional[SchemaPath]:
        if "oneOf" not in self.schema:
            return None

        one_of_schemas = self.schema / "oneOf"
        for subschema in one_of_schemas:
            validator = self.evolve(subschema)
            try:
                validator.validate(value)
            except ValidateError:
                continue
            else:
                return subschema

        log.warning("valid oneOf schema not found")
        return None

    def iter_any_of_schemas(
        self,
        value: Any,
    ) -> Iterator[SchemaPath]:
        if "anyOf" not in self.schema:
            return

        any_of_schemas = self.schema / "anyOf"
        for subschema in any_of_schemas:
            validator = self.evolve(subschema)
            try:
                validator.validate(value)
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
