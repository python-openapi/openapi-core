import logging
from functools import cached_property
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Optional

from jsonschema.exceptions import FormatError
from jsonschema.protocols import Validator
from jsonschema_path import SchemaPath

from openapi_core.validation.schemas.datatypes import (
    _EMPTY_STATE_TUPLE as _EMPTY_STATES_TUPLE,
)
from openapi_core.validation.schemas.datatypes import (
    _EMPTY_STATES as _EMPTY_STATES_MAP,
)
from openapi_core.validation.schemas.datatypes import FormatValidator
from openapi_core.validation.schemas.datatypes import ValidationState
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.schemas.exceptions import ValidateError

# OpenAPI ``format`` values whose *type: string* schemas are permitted to
# carry a raw ``bytes`` payload end-to-end -- ``binary`` for opaque file
# bodies (multipart/form-data, application/octet-stream) and ``byte`` for
# base64 strings that callers may still hand in as ``bytes``.
_BINARY_STRING_FORMATS = frozenset({"binary", "byte"})

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
        # OpenAPI allows ``bytes`` to flow through ``string`` schemas
        # whose ``format`` is ``binary`` or ``byte`` (file uploads,
        # base64-encoded blobs). jsonschema only validates ``string``
        # against text, so we present it a decoded view while keeping
        # the original ``value`` for downstream unmarshalling and error
        # reporting.
        normalized = self._normalize_for_validation(value)
        errors_iter = self.validator.iter_errors(normalized)
        errors = tuple(errors_iter)
        if errors:
            schema_type = (self.schema / "type").read_str_or_list("any")
            raise InvalidSchemaValue(value, schema_type, schema_errors=errors)

    @staticmethod
    def _decode_binary_value(value: bytes) -> str:
        """Decode raw ``bytes`` into the text view jsonschema expects.

        ``utf-8`` first because that's what the vast majority of byte
        bodies actually are; falling back to ASCII + ``surrogateescape``
        guarantees the call never raises for arbitrary binary payloads
        (a real file upload may contain any byte sequence).
        """
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("ASCII", errors="surrogateescape")

    def _accepts_binary_string(self, value: Any) -> bool:
        """True when ``value`` is ``bytes`` and the schema at this
        position is a ``string`` whose ``format`` allows raw bytes.
        """
        if not isinstance(value, bytes):
            return False
        schema_format = (self.schema / "format").read_str(None)
        if schema_format not in _BINARY_STRING_FORMATS:
            return False
        schema_types = (self.schema / "type").read_str_or_list(None)
        if schema_types is None:
            # No declared type: OAS 3.1 lets any value flow; treat the
            # binary/byte format as authoritative.
            return True
        if isinstance(schema_types, str):
            return schema_types == "string"
        return "string" in schema_types

    def _normalize_for_validation(self, value: Any) -> Any:
        """Return a view of ``value`` with ``bytes`` decoded to text
        wherever the schema-at-this-position is a binary/byte string.

        The original ``value`` is never mutated. Containers are only
        copied when a descendant actually changes, so the unchanged
        fast path returns ``value`` itself -- callers can use object
        identity to detect a no-op.

        Recursion is driven by the schema, not by introspecting the
        value: a ``dict`` is only descended when the schema declares
        ``properties``/``additionalProperties``, a ``list`` only when
        it declares ``items``, and composition (``oneOf``/``anyOf``/
        ``allOf``) is descended unconditionally because that's where
        a multipart binary branch typically lives.
        """
        if self._accepts_binary_string(value):
            return self._decode_binary_value(value)

        normalized: Any
        if isinstance(value, dict):
            normalized = self._normalize_mapping_for_validation(value)
        elif isinstance(value, list) and "items" in self.schema:
            normalized = self._normalize_array_for_validation(value)
        else:
            normalized = value

        # Composition keywords are where the binary branch actually
        # lives in real specs (a multipart oneOf with a file branch and
        # a non-file branch, for example). We apply each sub-schema's
        # normalization in turn -- idempotent because a sub-schema that
        # doesn't touch a position returns the same object, and once a
        # bytes value has been decoded to ``str`` no other sub-schema
        # treats it as binary.
        for keyword in ("oneOf", "anyOf", "allOf"):
            if keyword not in self.schema:
                continue
            for subschema in self.schema / keyword:
                normalized = self.evolve(subschema)._normalize_for_validation(
                    normalized
                )

        return normalized

    def _normalize_mapping_for_validation(
        self, value: dict[str, Any]
    ) -> dict[str, Any]:
        normalized: dict[str, Any] = value

        if "properties" in self.schema:
            for prop_name, prop_schema in (self.schema / "properties").items():
                if not isinstance(prop_name, str) or prop_name not in value:
                    continue
                prop_validator = self.evolve(prop_schema)
                new_value = prop_validator._normalize_for_validation(
                    value[prop_name]
                )
                if new_value is value[prop_name]:
                    continue
                if normalized is value:
                    normalized = dict(value)
                normalized[prop_name] = new_value

        additional = self.schema.get("additionalProperties", True)
        if additional in (True, False):
            return normalized

        property_names: set[str] = set()
        if "properties" in self.schema:
            property_names = {
                name
                for name in (self.schema / "properties").keys()
                if isinstance(name, str)
            }
        additional_validator = self.evolve(
            self.schema / "additionalProperties"
        )
        for prop_name, prop_value in value.items():
            if prop_name in property_names:
                continue
            new_value = additional_validator._normalize_for_validation(
                prop_value
            )
            if new_value is prop_value:
                continue
            if normalized is value:
                normalized = dict(value)
            normalized[prop_name] = new_value

        return normalized

    def _normalize_array_for_validation(self, value: list[Any]) -> list[Any]:
        items_validator = self.evolve(self.schema / "items")
        normalized: Optional[list[Any]] = None
        for idx, item in enumerate(value):
            new_item = items_validator._normalize_for_validation(item)
            if new_item is item:
                continue
            if normalized is None:
                normalized = list(value)
            normalized[idx] = new_item
        if normalized is None:
            return value
        return normalized

    # Cache the recursive "does this schema benefit from a ValidationState?"
    # check, keyed on the SchemaPath. Under jsonschema-path 0.5 (pathable
    # 0.6) SchemaPath is an AccessorPath whose identity is
    # (parts, accessor), and SchemaAccessor in turn hashes/compares on
    # id(node) and id(path_resolver). The key is therefore effectively
    # per-resolver: two SchemaPaths share a cache slot only when they
    # address the same location *within the same loaded spec*, never
    # across distinct specs that merely share a JSON-pointer path.
    # Entries are bounded by the number of distinct schema shapes per
    # spec and become collectable once the owning resolver is GC'd.
    _needs_state_cache: dict[SchemaPath, bool] = {}

    @classmethod
    def _schema_needs_state(cls, schema: SchemaPath) -> bool:
        """True if building a ValidationState for ``schema`` carries
        information the unmarshaller can reuse: either composition
        (oneOf/anyOf/allOf) on this node, or a descendant that does.

        Cycle-safe: a False sentinel is stored before recursing, so a
        $ref loop terminates and the real answer overwrites the
        sentinel once the recursion completes.
        """
        cache = cls._needs_state_cache
        cached = cache.get(schema)
        if cached is not None:
            return cached
        # Self-composition is the strongest signal; check it first to
        # short-circuit the cheap case.
        if "oneOf" in schema or "anyOf" in schema or "allOf" in schema:
            cache[schema] = True
            return True
        # Seed the in-progress sentinel for cycle protection.
        cache[schema] = False
        # Recurse into children. We only need to find one descendant
        # that needs state to flip our own answer.
        result = False
        if "properties" in schema:
            prop_iter = (schema / "properties").items()
            for prop_name, prop_schema in prop_iter:
                if not isinstance(prop_name, str):
                    continue
                if cls._schema_needs_state(prop_schema):
                    result = True
                    break
        if not result and "additionalProperties" in schema:
            try:
                ap = schema / "additionalProperties"
            except Exception:
                ap = None
            if ap is not None and cls._schema_needs_state(ap):
                result = True
        if not result and "items" in schema:
            try:
                items = schema / "items"
            except Exception:
                items = None
            if items is not None and cls._schema_needs_state(items):
                result = True
        cache[schema] = result
        return result

    def validate_state(self, value: Any) -> ValidationState:
        self.validate(value)
        return self._build_trusted_state(value)

    def _build_trusted_state(self, value: Any) -> ValidationState:
        """Build a ValidationState for ``value`` against ``self.schema``.

        Pre-condition: ``value`` has already been validated against the
        schema (typically by an outer ``validate_state``). This method
        does NOT re-validate -- it only records the composition-branch
        decisions and recurses into children that themselves need
        state.
        """
        primitive_type = self.get_primitive_type(value)
        property_states: Mapping[str, ValidationState] = _EMPTY_STATES_MAP
        additional_property_states: Mapping[str, ValidationState] = (
            _EMPTY_STATES_MAP
        )
        item_states: tuple[ValidationState, ...] = _EMPTY_STATES_TUPLE
        one_of_state: Optional[ValidationState] = None
        any_of_states: tuple[ValidationState, ...] = _EMPTY_STATES_TUPLE
        all_of_states: tuple[ValidationState, ...] = _EMPTY_STATES_TUPLE

        # Composition keywords: always cache the branch selection,
        # because re-resolving it at unmarshal time is exactly the work
        # ValidationState exists to avoid.
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

        # Children: recurse only into sub-trees that themselves contain
        # composition. Sub-trees without composition can be unmarshalled
        # via the bare-state fast path -- no cached state needed.
        if primitive_type == "object" and isinstance(value, dict):
            new_props: dict[str, ValidationState] = {}
            for prop_name, prop_schema in self._get_input_properties(
                value
            ).items():
                if not self._schema_needs_state(prop_schema):
                    continue
                new_props[prop_name] = self.evolve(
                    prop_schema
                )._build_trusted_state(value[prop_name])
            if new_props:
                property_states = new_props

            new_addl: dict[str, ValidationState] = {}
            for (
                prop_name,
                additional_prop_schema,
            ) in self._get_input_additional_properties(value).items():
                if not self._schema_needs_state(additional_prop_schema):
                    continue
                new_addl[prop_name] = self.evolve(
                    additional_prop_schema
                )._build_trusted_state(value[prop_name])
            if new_addl:
                additional_property_states = new_addl
        elif primitive_type == "array" and isinstance(value, list):
            # Skip per-item state when the item schema itself doesn't
            # need state -- the unmarshaller's bare-state fast path
            # handles each item.
            built = self._build_item_states_if_needed(value)
            if built:
                item_states = built

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

    def _build_item_states_if_needed(
        self, value: list[Any]
    ) -> tuple[ValidationState, ...]:
        if "items" not in self.schema:
            return _EMPTY_STATES_TUPLE
        items_schema = self.schema / "items"
        if not self._schema_needs_state(items_schema):
            return _EMPTY_STATES_TUPLE
        item_validator = self.evolve(items_schema)
        return tuple(
            item_validator._build_trusted_state(item) for item in value
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
            if schema_type == "string" and self._accepts_binary_string(value):
                # Bytes value, binary/byte format, ``string`` is in the
                # declared type list: treat it as string without asking
                # jsonschema's type checker (which doesn't know about
                # OpenAPI's binary convention).
                return "string"
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
