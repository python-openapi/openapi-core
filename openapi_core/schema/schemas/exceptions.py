import attr

from openapi_core.schema.exceptions import OpenAPIMappingError


class OpenAPISchemaError(OpenAPIMappingError):
    pass


class ValidateError(OpenAPISchemaError):
    """Schema validate operation error"""
    pass


@attr.s(hash=True)
class InvalidSchemaValue(ValidateError):
    value = attr.ib()
    type = attr.ib()
    _schema_errors = attr.ib(default=None)
    _schema_errors_iter = attr.ib(factory=list)

    @property
    def schema_errors(self):
        if self._schema_errors is None:
            self._schema_errors = list(self._schema_errors_iter)
        return self._schema_errors

    def __str__(self):
        return (
            "Value {value} not valid for schema of type {type}: {errors}"
        ).format(value=self.value, type=self.type, errors=self.schema_errors)
