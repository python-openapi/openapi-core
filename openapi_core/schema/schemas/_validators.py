from jsonschema._utils import find_additional_properties, extras_msg
from jsonschema.exceptions import ValidationError, FormatError


def type(validator, data_type, instance, schema):
    if instance is None:
        return

    if not validator.is_type(instance, data_type):
        yield ValidationError("%r is not of type %s" % (instance, data_type))


def format(validator, format, instance, schema):
    if instance is None:
        return

    if validator.format_checker is not None:
        try:
            validator.format_checker.check(instance, format)
        except FormatError as error:
            yield ValidationError(error.message, cause=error.cause)


def items(validator, items, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    for index, item in enumerate(instance):
        for error in validator.descend(item, items, path=index):
            yield error


def nullable(validator, is_nullable, instance, schema):
    if instance is None and not is_nullable:
        yield ValidationError("None for not nullable")


def additionalProperties(validator, aP, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    extras = set(find_additional_properties(instance, schema))

    if not extras:
        return

    if validator.is_type(aP, "object"):
        for extra in extras:
            for error in validator.descend(instance[extra], aP, path=extra):
                yield error
    elif validator.is_type(aP, "boolean"):
        if not aP:
            error = "Additional properties are not allowed (%s %s unexpected)"
            yield ValidationError(error % extras_msg(extras))


def not_implemented(validator, value, instance, schema):
    pass
