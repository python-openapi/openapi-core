from base64 import b64encode, b64decode
import binascii
from datetime import datetime
from uuid import UUID

from jsonschema._format import FormatChecker
from jsonschema.exceptions import FormatError
from six import binary_type, text_type, integer_types

DATETIME_HAS_STRICT_RFC3339 = False
DATETIME_HAS_ISODATE = False
DATETIME_RAISES = ()

try:
    import isodate
except ImportError:
    pass
else:
    DATETIME_HAS_ISODATE = True
    DATETIME_RAISES += (ValueError, isodate.ISO8601Error)

try:
    import strict_rfc3339
except ImportError:
    pass
else:
    DATETIME_HAS_STRICT_RFC3339 = True
    DATETIME_RAISES += (ValueError, TypeError)


class StrictFormatChecker(FormatChecker):

    def check(self, instance, format):
        if format not in self.checkers:
            raise FormatError(
                "Format checker for %r format not found" % (format, ))
        return super(StrictFormatChecker, self).check(
            instance, format)


oas30_format_checker = StrictFormatChecker()


@oas30_format_checker.checks('int32')
def is_int32(instance):
    return isinstance(instance, integer_types)


@oas30_format_checker.checks('int64')
def is_int64(instance):
    return isinstance(instance, integer_types)


@oas30_format_checker.checks('float')
def is_float(instance):
    return isinstance(instance, float)


@oas30_format_checker.checks('double')
def is_double(instance):
    # float has double precision in Python
    # It's double in CPython and Jython
    return isinstance(instance, float)


@oas30_format_checker.checks('binary')
def is_binary(instance):
    return isinstance(instance, binary_type)


@oas30_format_checker.checks('byte', raises=(binascii.Error, TypeError))
def is_byte(instance):
    if isinstance(instance, text_type):
        instance = instance.encode()

    return b64encode(b64decode(instance)) == instance


@oas30_format_checker.checks("date-time", raises=DATETIME_RAISES)
def is_datetime(instance):
    if isinstance(instance, binary_type):
        return False
    if not isinstance(instance, text_type):
        return True
    
    if DATETIME_HAS_STRICT_RFC3339:
        return strict_rfc3339.validate_rfc3339(instance)
    
    if DATETIME_HAS_ISODATE:
        return isodate.parse_datetime(instance)

    return True


@oas30_format_checker.checks("date", raises=ValueError)
def is_date(instance):
    if isinstance(instance, binary_type):
        return False
    if not isinstance(instance, text_type):
        return True
    return datetime.strptime(instance, "%Y-%m-%d")


@oas30_format_checker.checks("uuid", raises=AttributeError)
def is_uuid(instance):
    if isinstance(instance, binary_type):
        return False
    if not isinstance(instance, text_type):
        return True
    try:
        uuid_obj = UUID(instance)
    except ValueError:
        return False

    return text_type(uuid_obj) == instance
