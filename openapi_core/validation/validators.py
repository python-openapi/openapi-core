"""OpenAPI core validation validators module"""
from openapi_core.unmarshalling.schemas.util import build_format_checker


class BaseValidator(object):

    def __init__(
            self, spec,
            base_url=None,
            custom_formatters=None, custom_media_type_deserializers=None,
    ):
        self.spec = spec
        self.base_url = base_url
        self.custom_formatters = custom_formatters or {}
        self.custom_media_type_deserializers = custom_media_type_deserializers

        self.format_checker = build_format_checker(**self.custom_formatters)

    def _find_path(self, request):
        from openapi_core.templating.paths.finders import PathFinder
        finder = PathFinder(self.spec, base_url=self.base_url)
        return finder.find(request)

    def _deserialise_media_type(self, media_type, value):
        from openapi_core.deserializing.media_types.factories import (
            MediaTypeDeserializersFactory,
        )
        deserializers_factory = MediaTypeDeserializersFactory(
            self.custom_media_type_deserializers)
        deserializer = deserializers_factory.create(media_type)
        return deserializer(value)

    def _cast(self, param_or_media_type, value):
        # return param_or_media_type.cast(value)
        if not param_or_media_type.schema:
            return value

        from openapi_core.casting.schemas.factories import SchemaCastersFactory
        casters_factory = SchemaCastersFactory()
        caster = casters_factory.create(param_or_media_type.schema)
        return caster(value)

    def _unmarshal(self, param_or_media_type, value, context):
        if not param_or_media_type.schema:
            return value

        from openapi_core.unmarshalling.schemas.factories import (
            SchemaUnmarshallersFactory,
        )
        unmarshallers_factory = SchemaUnmarshallersFactory(
            self.spec._resolver, self.format_checker,
            self.custom_formatters, context=context,
        )
        unmarshaller = unmarshallers_factory.create(
            param_or_media_type.schema)
        return unmarshaller(value)
