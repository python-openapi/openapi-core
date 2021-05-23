from typing import Dict, Optional, Type
import warnings

from openapi_schema_validator import OAS30Validator

from openapi_core.spec.paths import SpecPath
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    FormatterNotFoundError,
)
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.unmarshallers import (
    StringUnmarshaller, IntegerUnmarshaller, NumberUnmarshaller,
    BooleanUnmarshaller, ArrayUnmarshaller, ObjectUnmarshaller,
    AnyUnmarshaller, PrimitiveTypeUnmarshaller,
)


class SchemaUnmarshallersFactory:

    UNMARSHALLERS = {
        'string': StringUnmarshaller,
        'integer': IntegerUnmarshaller,
        'number': NumberUnmarshaller,
        'boolean': BooleanUnmarshaller,
        'array': ArrayUnmarshaller,
        'object': ObjectUnmarshaller,
        'any': AnyUnmarshaller,
    }

    COMPLEX_UNMARSHALLERS = ['array', 'object', 'any']

    CONTEXT_VALIDATION = {
        UnmarshalContext.REQUEST: 'write',
        UnmarshalContext.RESPONSE: 'read',
    }

    def __init__(
        self,
        resolver=None,
        format_checker=None,
        custom_formatters: Optional[Dict[str, Formatter]] = None,
        context=None,
    ):
        self.resolver = resolver
        self.format_checker = format_checker
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters
        self.context = context

    def create(
        self,
        schema: SpecPath,
        type_override: Optional[str] = None,
    ) -> PrimitiveTypeUnmarshaller:
        """Create unmarshaller from the schema."""
        if schema is None:
            raise TypeError("Invalid schema")

        if schema.getkey('deprecated', False):
            warnings.warn("The schema is deprecated", DeprecationWarning)

        schema_type = type_override or schema.getkey('type', 'any')
        schema_format = schema.getkey('format')

        klass: Type[PrimitiveTypeUnmarshaller] = self.UNMARSHALLERS[
            schema_type]

        formatter = self.get_formatter(schema_format, klass.FORMATTERS)
        if formatter is None:
            raise FormatterNotFoundError(schema_format)

        validator = self.get_validator(schema)

        kwargs: Dict = dict()
        if schema_type in self.COMPLEX_UNMARSHALLERS:
            kwargs.update(
                unmarshallers_factory=self,
                context=self.context,
            )
        return klass(schema, formatter, validator, **kwargs)

    def get_formatter(
        self,
        type_format: str,
        default_formatters: Dict[Optional[str], Formatter],
    ) -> Optional[Formatter]:
        try:
            return self.custom_formatters[type_format]
        except KeyError:
            return default_formatters.get(type_format)

    def get_validator(self, schema: SpecPath) -> OAS30Validator:
        kwargs = {
            'resolver': self.resolver,
            'format_checker': self.format_checker,
        }
        if self.context is not None:
            kwargs[self.CONTEXT_VALIDATION[self.context]] = True
        with schema.open() as schema_dict:
            return OAS30Validator(schema_dict, **kwargs)
