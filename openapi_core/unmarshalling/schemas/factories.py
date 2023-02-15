import sys
import warnings
from typing import Optional

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backports.cached_property import cached_property

from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.datatypes import CustomFormattersDict
from openapi_core.unmarshalling.schemas.datatypes import FormatUnmarshaller
from openapi_core.unmarshalling.schemas.datatypes import UnmarshallersDict
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.unmarshallers import (
    FormatsUnmarshaller,
)
from openapi_core.unmarshalling.schemas.unmarshallers import SchemaUnmarshaller
from openapi_core.unmarshalling.schemas.unmarshallers import TypesUnmarshaller
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory


class SchemaUnmarshallersFactory:
    def __init__(
        self,
        schema_validators_factory: SchemaValidatorsFactory,
        types_unmarshaller: TypesUnmarshaller,
        format_unmarshallers: Optional[UnmarshallersDict] = None,
        custom_formatters: Optional[CustomFormattersDict] = None,
    ):
        self.schema_validators_factory = schema_validators_factory
        self.types_unmarshaller = types_unmarshaller
        if custom_formatters is None:
            custom_formatters = {}
        if format_unmarshallers is None:
            format_unmarshallers = {}
        self.format_unmarshallers = format_unmarshallers
        self.custom_formatters = custom_formatters

    @cached_property
    def formats_unmarshaller(self) -> FormatsUnmarshaller:
        return FormatsUnmarshaller(
            self.format_unmarshallers,
            self.custom_formatters,
        )

    def create(self, schema: Spec) -> SchemaUnmarshaller:
        """Create unmarshaller from the schema."""
        if schema is None:
            raise TypeError("Invalid schema")

        if schema.getkey("deprecated", False):
            warnings.warn("The schema is deprecated", DeprecationWarning)

        formatters_checks = {
            name: formatter.validate
            for name, formatter in self.custom_formatters.items()
        }
        schema_validator = self.schema_validators_factory.create(
            schema, **formatters_checks
        )

        schema_format = schema.getkey("format")

        # FIXME: don;t raise exception on unknown format
        if (
            schema_format
            and schema_format
            not in self.schema_validators_factory.format_checker.checkers
            and schema_format not in self.custom_formatters
        ):
            raise FormatterNotFoundError(schema_format)

        return SchemaUnmarshaller(
            schema,
            schema_validator,
            self.types_unmarshaller,
            self.formats_unmarshaller,
        )
