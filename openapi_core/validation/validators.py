"""OpenAPI core validation validators module"""
from typing import Any, Callable, Dict, List, Optional, Union

from werkzeug.datastructures import ImmutableMultiDict, Headers

from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.parameters.factories import (
    ParameterDeserializersFactory,
)
from openapi_core.schema.parameters import get_value
from openapi_core.spec.paths import SpecPath
from openapi_core.templating.media_types.datatypes import MediaTypeResult
from openapi_core.templating.paths.datatypes import ServerResult
from openapi_core.templating.paths.finders import PathFinder
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.unmarshalling.schemas.util import build_format_checker


class BaseValidator:

    def __init__(
        self,
        spec: SpecPath,
        base_url: Optional[str] = None,
        custom_formatters: Optional[Dict[str, Formatter]] = None,
        custom_media_type_deserializers: Optional[Dict[str, Callable]] = None,
    ):
        self.spec = spec
        self.base_url = base_url
        self.custom_formatters = custom_formatters or {}
        self.custom_media_type_deserializers = custom_media_type_deserializers

        self.format_checker = build_format_checker(**self.custom_formatters)

    @property
    def path_finder(self) -> PathFinder:
        return PathFinder(self.spec, base_url=self.base_url)

    @property
    def schema_casters_factory(self) -> SchemaCastersFactory:
        return SchemaCastersFactory()

    @property
    def media_type_deserializers_factory(self) -> MediaTypeDeserializersFactory:
        return MediaTypeDeserializersFactory(
            self.custom_media_type_deserializers)

    @property
    def parameter_deserializers_factory(self) -> ParameterDeserializersFactory:
        return ParameterDeserializersFactory()

    @property
    def schema_unmarshallers_factory(self):
        raise NotImplementedError

    def _find_path(self, request) -> ServerResult:
        return self.path_finder.find(request)

    def _get_media_type(self, content, request_or_response) -> MediaTypeResult:
        from openapi_core.templating.media_types.finders import MediaTypeFinder
        finder = MediaTypeFinder(content)
        return finder.find(request_or_response)

    def _deserialise_data(
        self,
        mimetype: str,
        value: str,
    ) -> Union[str, dict]:
        deserializer = self.media_type_deserializers_factory.create(mimetype)
        return deserializer(value)

    def _deserialise_parameter(
        self,
        param: SpecPath,
        value: Optional[Union[str, List[str]]],
    ) -> Optional[Union[str, List[str]]]:
        deserializer = self.parameter_deserializers_factory.create(param)
        return deserializer(value)

    def _cast(
        self,
        schema: SpecPath,
        value: Optional[Union[str, list, dict]],
    ) -> Optional[Union[int, float, bool, str, list, dict]]:
        caster = self.schema_casters_factory.create(schema)
        return caster(value)

    def _unmarshal(
        self,
        schema: SpecPath,
        value: Optional[Union[int, float, bool, str, list, dict]],
    ) -> Any:
        unmarshaller = self.schema_unmarshallers_factory.create(schema)
        return unmarshaller(value)

    def _get_param_or_header_value(
        self,
        param_or_header: SpecPath,
        location: Union[Dict, ImmutableMultiDict, Headers],
        name: Optional[str] = None,
    ) -> Any:
        schema: SpecPath
        try:
            raw_value = get_value(param_or_header, location, name=name)
        except KeyError:
            if 'schema' not in param_or_header:
                raise
            schema = param_or_header / 'schema'
            if 'default' not in schema:
                raise
            casted = schema['default']
        else:
            deserialised: Optional[Union[str, list, dict]]
            # Simple scenario
            if 'content' not in param_or_header:
                assert isinstance(raw_value, (str, list, type(None)))
                deserialised = self._deserialise_parameter(
                    param_or_header, raw_value)
                schema = param_or_header / 'schema'
            # Complex scenario
            else:
                assert isinstance(raw_value, str)
                content: SpecPath = param_or_header / 'content'
                mimetype: str
                media_type: SpecPath
                mimetype, media_type = next(content.items())
                deserialised = self._deserialise_data(mimetype, raw_value)
                schema = media_type / 'schema'
            casted = self._cast(schema, deserialised)
        unmarshalled = self._unmarshal(schema, casted)
        return unmarshalled
