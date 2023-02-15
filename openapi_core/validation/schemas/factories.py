from copy import deepcopy
from typing import Mapping
from typing import Optional
from typing import Type

from jsonschema._format import FormatChecker
from jsonschema.protocols import Validator

from openapi_core.spec import Spec
from openapi_core.validation.schemas.datatypes import FormatValidator
from openapi_core.validation.schemas.validators import SchemaValidator


class SchemaValidatorsFactory:
    def __init__(
        self,
        schema_validator_class: Type[Validator],
        format_checker: Optional[FormatChecker] = None,
    ):
        self.schema_validator_class = schema_validator_class
        if format_checker is None:
            format_checker = self.schema_validator_class.FORMAT_CHECKER
        self.format_checker = format_checker

    def get_format_checker(
        self, **format_checks: FormatValidator
    ) -> FormatChecker:
        format_checker = deepcopy(self.format_checker)
        for name, check in format_checks.items():
            format_checker.checks(name)(check)
        return format_checker

    def create(
        self, schema: Spec, **format_checks: FormatValidator
    ) -> Validator:
        format_checker = self.get_format_checker(**format_checks)
        resolver = schema.accessor.resolver  # type: ignore
        with schema.open() as schema_dict:
            jsonschema_validator = self.schema_validator_class(
                schema_dict,
                resolver=resolver,
                format_checker=format_checker,
            )

        return SchemaValidator(schema, jsonschema_validator)
