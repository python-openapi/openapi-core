import sys
from copy import deepcopy
from functools import partial
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Type

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backports.cached_property import cached_property
from jsonschema._format import FormatChecker
from jsonschema.protocols import Validator

from openapi_core.spec import Spec
from openapi_core.unmarshalling.schemas.datatypes import CustomFormattersDict
from openapi_core.validation.schemas.datatypes import FormatValidator
from openapi_core.validation.schemas.util import build_format_checker
from openapi_core.validation.schemas.validators import SchemaValidator


class SchemaValidatorsFactory:
    def __init__(
        self,
        schema_validator_class: Type[Validator],
        format_checker: Optional[FormatChecker] = None,
        formatters: Optional[CustomFormattersDict] = None,
        custom_formatters: Optional[CustomFormattersDict] = None,
    ):
        self.schema_validator_class = schema_validator_class
        if format_checker is None:
            format_checker = self.schema_validator_class.FORMAT_CHECKER
        self.format_checker = deepcopy(format_checker)
        if formatters is None:
            formatters = {}
        self.formatters = formatters
        if custom_formatters is None:
            custom_formatters = {}
        self.custom_formatters = custom_formatters

    def add_checks(self, **format_checks) -> None:
        for name, check in format_checks.items():
            self.format_checker.checks(name)(check)

    def get_checker(self, name: str) -> FormatValidator:
        if name in self.format_checker.checkers:
            return partial(self.format_checker.check, format=name)

        return lambda x: True

    def create(self, schema: Spec) -> Validator:
        resolver = schema.accessor.resolver  # type: ignore
        with schema.open() as schema_dict:
            jsonschema_validator = self.schema_validator_class(
                schema_dict,
                resolver=resolver,
                format_checker=self.format_checker,
            )

        return SchemaValidator(schema, jsonschema_validator)
