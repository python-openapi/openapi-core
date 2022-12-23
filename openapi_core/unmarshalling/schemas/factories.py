import sys
import warnings
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Type
from typing import Union

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backports.cached_property import cached_property
from jsonschema.protocols import Validator
from openapi_schema_validator import OAS30Validator

from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.datatypes import CustomFormattersDict
from openapi_core.unmarshalling.schemas.datatypes import FormattersDict
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
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

    CONTEXTS = {
        UnmarshalContext.REQUEST: "write",
        UnmarshalContext.RESPONSE: "read",
    }

    def __init__(
        self,
        schema_validator_class: Type[Validator],
        custom_formatters: Optional[CustomFormattersDict] = None,
        context: Optional[UnmarshalContext] = None,
    ):
        self.schema_validator_class = schema_validator_class
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters
        self.context = context

    def create(self, schema: Spec) -> Validator:
        resolver = schema.accessor.resolver  # type: ignore
        custom_format_checks = {
            name: formatter.validate
            for name, formatter in self.custom_formatters.items()
        }
        format_checker = build_format_checker(**custom_format_checks)
        kwargs = {
            "resolver": resolver,
            "format_checker": format_checker,
        }
        if self.context is not None:
            kwargs[self.CONTEXTS[self.context]] = True
        with schema.open() as schema_dict:
            return self.schema_validator_class(schema_dict, **kwargs)


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
        custom_formatters: Optional[CustomFormattersDict] = None,
        context: Optional[UnmarshalContext] = None,
    ):
        self.schema_validator_class = schema_validator_class
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters
        self.context = context

    @cached_property
    def validators_factory(self) -> SchemaValidatorsFactory:
        return SchemaValidatorsFactory(
            self.schema_validator_class,
            self.custom_formatters,
            self.context,
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
        formatter = self.custom_formatters.get(schema_format)

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
