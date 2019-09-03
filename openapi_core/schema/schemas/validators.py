from jsonschema import _legacy_validators, _format, _types, _utils, _validators
from jsonschema.validators import create

from openapi_core.schema.schemas import _types as oas_types
from openapi_core.schema.schemas import _validators as oas_validators


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


OAS30Validator = create(
    meta_schema=_utils.load_schema("draft4"),
    validators={
        u"multipleOf": _validators.multipleOf,
        u"maximum": _legacy_validators.maximum_draft3_draft4,
        u"exclusiveMaximum": _validators.exclusiveMaximum,
        u"minimum": _legacy_validators.minimum_draft3_draft4,
        u"exclusiveMinimum": _validators.exclusiveMinimum,
        u"maxLength": _validators.maxLength,
        u"minLength": _validators.minLength,
        u"pattern": _validators.pattern,
        u"maxItems": _validators.maxItems,
        u"minItems": _validators.minItems,
        u"uniqueItems": _validators.uniqueItems,
        u"maxProperties": _validators.maxProperties,
        u"minProperties": _validators.minProperties,
        u"required": _validators.required,
        u"enum": _validators.enum,
        # adjusted to OAS
        u"type": oas_validators.type,
        u"allOf": _validators.allOf,
        u"oneOf": _validators.oneOf,
        u"anyOf": _validators.anyOf,
        u"not": _validators.not_,
        u"items": oas_validators.items,
        u"properties": _validators.properties,
        u"additionalProperties": _validators.additionalProperties,
        # TODO: adjust description
        u"format": _validators.format,
        # TODO: adjust default
        u"$ref": _validators.ref,
        # fixed OAS fields
        u"nullable": oas_validators.nullable,
        u"discriminator": oas_validators.not_implemented,
        u"readOnly": oas_validators.not_implemented,
        u"writeOnly": oas_validators.not_implemented,
        u"xml": oas_validators.not_implemented,
        u"externalDocs": oas_validators.not_implemented,
        u"example": oas_validators.not_implemented,
        u"deprecated": oas_validators.not_implemented,
    },
    type_checker=oas_types.oas30_type_checker,
    version="oas30",
    id_of=lambda schema: schema.get(u"id", ""),
)
