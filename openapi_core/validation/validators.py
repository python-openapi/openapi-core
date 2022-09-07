"""OpenAPI core validation validators module"""
from urllib.parse import urljoin

from openapi_core.casting.schemas import schema_casters_factory
from openapi_core.deserializing.media_types import (
    media_type_deserializers_factory,
)
from openapi_core.deserializing.parameters import (
    parameter_deserializers_factory,
)
from openapi_core.schema.parameters import get_value
from openapi_core.templating.paths.finders import PathFinder
from openapi_core.unmarshalling.schemas.util import build_format_checker
from openapi_core.validation.request.protocols import SupportsPathPattern


class BaseValidator:
    def __init__(
        self,
        schema_unmarshallers_factory,
        schema_casters_factory=schema_casters_factory,
        parameter_deserializers_factory=parameter_deserializers_factory,
        media_type_deserializers_factory=media_type_deserializers_factory,
    ):
        self.schema_unmarshallers_factory = schema_unmarshallers_factory
        self.schema_casters_factory = schema_casters_factory
        self.parameter_deserializers_factory = parameter_deserializers_factory
        self.media_type_deserializers_factory = (
            media_type_deserializers_factory
        )

    def _find_path(self, spec, request, base_url=None):
        path_finder = PathFinder(spec, base_url=base_url)
        path_pattern = getattr(request, "path_pattern", None)
        return path_finder.find(
            request.method, request.host_url, request.path, path_pattern
        )

    def _get_media_type(self, content, mimetype):
        from openapi_core.templating.media_types.finders import MediaTypeFinder

        finder = MediaTypeFinder(content)
        return finder.find(mimetype)

    def _deserialise_data(self, mimetype, value):
        deserializer = self.media_type_deserializers_factory.create(mimetype)
        return deserializer(value)

    def _deserialise_parameter(self, param, value):
        deserializer = self.parameter_deserializers_factory.create(param)
        return deserializer(value)

    def _cast(self, schema, value):
        caster = self.schema_casters_factory.create(schema)
        return caster(value)

    def _unmarshal(self, schema, value):
        unmarshaller = self.schema_unmarshallers_factory.create(schema)
        return unmarshaller(value)

    def _get_param_or_header_value(self, param_or_header, location, name=None):
        try:
            raw_value = get_value(param_or_header, location, name=name)
        except KeyError:
            if "schema" not in param_or_header:
                raise
            schema = param_or_header / "schema"
            if "default" not in schema:
                raise
            casted = schema["default"]
        else:
            # Simple scenario
            if "content" not in param_or_header:
                deserialised = self._deserialise_parameter(
                    param_or_header, raw_value
                )
                schema = param_or_header / "schema"
            # Complex scenario
            else:
                content = param_or_header / "content"
                mimetype, media_type = next(content.items())
                deserialised = self._deserialise_data(mimetype, raw_value)
                schema = media_type / "schema"
            casted = self._cast(schema, deserialised)
        unmarshalled = self._unmarshal(schema, casted)
        return unmarshalled
