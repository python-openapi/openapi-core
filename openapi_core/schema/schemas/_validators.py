from jsonschema.exceptions import ValidationError


def type(validator, data_type, instance, schema):
    if instance is None:
        return

    if not validator.is_type(instance, data_type):
        yield ValidationError("%r is not of type %s" % (instance, data_type))


def items(validator, items, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    for index, item in enumerate(instance):
        for error in validator.descend(item, items, path=index):
            yield error


def nullable(validator, is_nullable, instance, schema):
    if instance is None and not is_nullable:
        yield ValidationError("None for not nullable")


def not_implemented(validator, value, instance, schema):
    pass
