from jsonschema import validators
from jsonschema.validators import Draft4Validator


class TypeValidator(object):

    def __init__(self, *types, **options):
        self.types = types
        self.exclude = options.get('exclude')

    def __call__(self, value):
        if self.exclude is not None and isinstance(value, self.exclude):
            return False

        if not isinstance(value, self.types):
            return False

        return True


class AttributeValidator(object):

    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, value):
        if not hasattr(value, self.attribute):
            return False

        return True


class Draft4ExtendedValidatorFactory(Draft4Validator):
    """Draft4Validator with extra validators factory."""

    @classmethod
    def create(cls):
        """Creates a customized Draft4ExtendedValidator."""
        spec_validators = cls._get_spec_validators()
        return validators.extend(Draft4Validator, spec_validators)

    @classmethod
    def _get_spec_validators(cls):
        from jsonschema import _validators

        return {
            '$ref': _validators.ref,
            'properties': _validators.properties_draft4,
            'additionalProperties': _validators.additionalProperties,
            'patternProperties': _validators.patternProperties,
            'type': _validators.type_draft4,
            'dependencies': _validators.dependencies,
            'required': _validators.required_draft4,
            'minProperties': _validators.minProperties_draft4,
            'maxProperties': _validators.maxProperties_draft4,
            'allOf': _validators.allOf_draft4,
            'oneOf': _validators.oneOf_draft4,
            'anyOf': _validators.anyOf_draft4,
            'not': _validators.not_draft4,
        }



class SchemaValidator(object):

    def __init__(self, spec_dict, schema_dict):
        self.spec_dict = spec_dict
        self.schema_dict = schema_dict

    def __call__(self, value):
        nullable = self.spec_dict.get('nullable', 'false')
        if nullable == 'true' and value is None:
            return True

        validator = self.validator_cls(self.schema_dict)
        validator.validate(value)
        return True

    def iter_errors(self, value):
        nullable = self.spec_dict.get('nullable', 'false')
        if nullable == 'true' and value is None:
            return

        validator = self.validator_cls(self.schema_dict)
        for err in validator.iter_errors(value):
            yield err

    @property
    def validator_cls(self):
        return Draft4ExtendedValidatorFactory.create()
