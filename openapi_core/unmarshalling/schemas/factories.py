import sys
import warnings
from functools import partial
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Type
from typing import Union

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backports.cached_property import cached_property
from jsonschema._format import FormatChecker
from jsonschema.protocols import Validator
from openapi_schema_validator import OAS30Validator

from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.datatypes import CustomFormattersDict
from openapi_core.unmarshalling.schemas.datatypes import FormattersDict
from openapi_core.unmarshalling.schemas.datatypes import UnmarshallersDict
from openapi_core.unmarshalling.schemas.enums import ValidationContext
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.unmarshallers import AnyUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import ArrayUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import (
    BaseSchemaUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import (
    BooleanUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import (
    ComplexUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import (
    IntegerUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import (
    MultiTypeUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import NullUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import NumberUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import ObjectUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import StringUnmarshaller
from openapi_core.unmarshalling.schemas.util import build_format_checker


class SchemaValidatorsFactory:
    def __init__(
        self,
        schema_validator_class: Type[Validator],
        base_format_checker: Optional[FormatChecker] = None,
        formatters: Optional[CustomFormattersDict] = None,
        format_unmarshallers: Optional[UnmarshallersDict] = None,
        custom_formatters: Optional[CustomFormattersDict] = None,
    ):
        self.schema_validator_class = schema_validator_class
        if base_format_checker is None:
            base_format_checker = self.schema_validator_class.FORMAT_CHECKER
        self.base_format_checker = base_format_checker
        if formatters is None:
            formatters = {}
        self.formatters = formatters
        if format_unmarshallers is None:
            format_unmarshallers = {}
        self.format_unmarshallers = format_unmarshallers
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters

    @cached_property
    def format_checker(self) -> FormatChecker:
        format_checks: Dict[str, Callable[[Any], bool]] = {
            name: formatter.validate
            for formatters_list in [self.formatters, self.custom_formatters]
            for name, formatter in formatters_list.items()
        }
        format_checks.update(
            {
                name: self._create_checker(name)
                for name, _ in self.format_unmarshallers.items()
            }
        )
        return build_format_checker(self.base_format_checker, **format_checks)

    def _create_checker(self, name: str) -> Callable[[Any], bool]:
        if name in self.base_format_checker.checkers:
            return partial(self.base_format_checker.check, format=name)

        return lambda x: True

    def get_checker(self, name: str) -> Callable[[Any], bool]:
        if name in self.format_checker.checkers:
            return partial(self.format_checker.check, format=name)

        return lambda x: True

    def create(self, schema: Spec) -> Validator:
        resolver = schema.accessor.resolver  # type: ignore
        with schema.open() as schema_dict:
            return self.schema_validator_class(
                schema_dict,
                resolver=resolver,
                format_checker=self.format_checker,
            )


class SchemaFormattersFactory:
    def __init__(
        self,
        validators_factory: SchemaValidatorsFactory,
        formatters: Optional[CustomFormattersDict] = None,
        format_unmarshallers: Optional[UnmarshallersDict] = None,
        custom_formatters: Optional[CustomFormattersDict] = None,
    ):
        self.validators_factory = validators_factory
        if formatters is None:
            formatters = {}
        self.formatters = formatters
        if format_unmarshallers is None:
            format_unmarshallers = {}
        self.format_unmarshallers = format_unmarshallers
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters

    def create(self, schema_format: str) -> Optional[Formatter]:
        if schema_format in self.custom_formatters:
            return self.custom_formatters[schema_format]
        if schema_format in self.formatters:
            return self.formatters[schema_format]
        if schema_format in self.format_unmarshallers:
            validate_callable = self.validators_factory.get_checker(
                schema_format
            )
            format_callable = self.format_unmarshallers[schema_format]
            return Formatter.from_callables(validate_callable, format_callable)

        return None


class SchemaUnmarshallersFactory:

    UNMARSHALLERS: Dict[str, Type[BaseSchemaUnmarshaller]] = {
        "string": StringUnmarshaller,
        "integer": IntegerUnmarshaller,
        "number": NumberUnmarshaller,
        "boolean": BooleanUnmarshaller,
        "array": ArrayUnmarshaller,
        "object": ObjectUnmarshaller,
        "null": NullUnmarshaller,
        "any": AnyUnmarshaller,
    }

    COMPLEX_UNMARSHALLERS: Dict[str, Type[ComplexUnmarshaller]] = {
        "array": ArrayUnmarshaller,
        "object": ObjectUnmarshaller,
        "any": AnyUnmarshaller,
    }

    def __init__(
        self,
        schema_validator_class: Type[Validator],
        base_format_checker: Optional[FormatChecker] = None,
        formatters: Optional[CustomFormattersDict] = None,
        format_unmarshallers: Optional[UnmarshallersDict] = None,
        custom_formatters: Optional[CustomFormattersDict] = None,
        context: Optional[ValidationContext] = None,
    ):
        self.schema_validator_class = schema_validator_class
        self.base_format_checker = base_format_checker
        if custom_formatters is None:
            custom_formatters = {}
        self.formatters = formatters
        if format_unmarshallers is None:
            format_unmarshallers = {}
        self.format_unmarshallers = format_unmarshallers
        self.custom_formatters = custom_formatters
        self.context = context

    @cached_property
    def validators_factory(self) -> SchemaValidatorsFactory:
        return SchemaValidatorsFactory(
            self.schema_validator_class,
            self.base_format_checker,
            self.formatters,
            self.format_unmarshallers,
            self.custom_formatters,
        )

    @cached_property
    def formatters_factory(self) -> SchemaFormattersFactory:
        return SchemaFormattersFactory(
            self.validators_factory,
            self.formatters,
            self.format_unmarshallers,
            self.custom_formatters,
        )

    def create(
        self, schema: Spec, type_override: Optional[str] = None
    ) -> BaseSchemaUnmarshaller:
        """Create unmarshaller from the schema."""
        if schema is None:
            raise TypeError("Invalid schema")

        if schema.getkey("deprecated", False):
            warnings.warn("The schema is deprecated", DeprecationWarning)

        validator = self.validators_factory.create(schema)

        schema_format = schema.getkey("format")
        formatter = self.formatters_factory.create(schema_format)

        schema_type = type_override or schema.getkey("type", "any")
        if isinstance(schema_type, Iterable) and not isinstance(
            schema_type, str
        ):
            return MultiTypeUnmarshaller(
                schema,
                validator,
                formatter,
                self.validators_factory,
                self,
                context=self.context,
            )
        if schema_type in self.COMPLEX_UNMARSHALLERS:
            complex_klass = self.COMPLEX_UNMARSHALLERS[schema_type]
            return complex_klass(
                schema,
                validator,
                formatter,
                self.validators_factory,
                self,
                context=self.context,
            )

        klass = self.UNMARSHALLERS[schema_type]
        return klass(
            schema,
            validator,
            formatter,
            self.validators_factory,
            self,
        )
