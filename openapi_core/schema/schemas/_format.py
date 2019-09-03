from jsonschema._format import FormatChecker
from six import binary_type

oas30_format_checker = FormatChecker()


@oas30_format_checker.checks('binary')
def binary(value):
    return isinstance(value, binary_type)
