"""OpenAPI core validation validators module"""
from openapi_core.validation.util import get_operation_pattern


class BaseValidator(object):

    def __init__(
            self, spec,
            custom_formatters=None, custom_media_type_deserializers=None,
    ):
        self.spec = spec
        self.custom_formatters = custom_formatters
        self.custom_media_type_deserializers = custom_media_type_deserializers

    def _find_path(self, request):
        operation_pattern = self._get_operation_pattern(request)

        path = self.spec[operation_pattern]
        path_variables = {}
        operation = self.spec.get_operation(operation_pattern, request.method)
        servers = path.servers or operation.servers or self.spec.servers
        server = servers[0]
        server_variables = {}

        return path, operation, server, path_variables, server_variables

    def _get_operation_pattern(self, request):
        server = self.spec.get_server(request.full_url_pattern)

        return get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

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
            self.spec._resolver, self.custom_formatters,
            context=context,
        )
        unmarshaller = unmarshallers_factory.create(
            param_or_media_type.schema)
        return unmarshaller(value)
