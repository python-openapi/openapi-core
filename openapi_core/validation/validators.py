"""OpenAPI core validation validators module"""
from __future__ import division

from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.templating.paths.finders import PathFinder
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

    @property
    def path_finder(self):
        return PathFinder(self.spec, base_url=self.base_url)

    @property
    def schema_casters_factory(self):
        return SchemaCastersFactory()

    @property
    def media_type_deserializers_factory(self):
        return MediaTypeDeserializersFactory(
            self.custom_media_type_deserializers)

    @property
    def schema_unmarshallers_factory(self):
        raise NotImplementedError

    def _find_path(self, request):
        return self.path_finder.find(request)

    def _get_media_type(self, content, request_or_response):
        from openapi_core.templating.media_types.finders import MediaTypeFinder
        finder = MediaTypeFinder(content)
        return finder.find(request_or_response)

    def _deserialise_data(self, mimetype, value):
        deserializer = self.media_type_deserializers_factory.create(mimetype)
        return deserializer(value)

    def _cast(self, param_or_media_type, value):
        # return param_or_media_type.cast(value)
        if 'schema' not in param_or_media_type:
            return value

        schema = param_or_media_type / 'schema'
        caster = self.schema_casters_factory.create(schema)
        return caster(value)

    def _unmarshal(self, param_or_media_type, value):
        if 'schema' not in param_or_media_type:
            return value

        schema = param_or_media_type / 'schema'
        unmarshaller = self.schema_unmarshallers_factory.create(schema)
        return unmarshaller(value)
