"""OpenAPI core validation validators module"""
import sys
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import Type
from urllib.parse import urljoin

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backports.cached_property import cached_property
from openapi_core.casting.schemas import schema_casters_factory
from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types import (
    media_type_deserializers_factory,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.parameters import (
    parameter_deserializers_factory,
)
from openapi_core.deserializing.parameters.factories import (
    ParameterDeserializersFactory,
)
from openapi_core.schema.parameters import get_value
from openapi_core.spec import Spec
from openapi_core.templating.media_types.datatypes import MediaType
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.finders import APICallPathFinder
from openapi_core.templating.paths.finders import BasePathFinder
from openapi_core.templating.paths.finders import WebhookPathFinder
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import SupportsPathPattern
from openapi_core.validation.request.protocols import WebhookRequest


class BaseValidator:

    schema_unmarshallers_factory: SchemaUnmarshallersFactory = NotImplemented

    def __init__(
        self,
        spec: Spec,
        base_url: Optional[str] = None,
        schema_unmarshallers_factory: Optional[
            SchemaUnmarshallersFactory
        ] = None,
        schema_casters_factory: SchemaCastersFactory = schema_casters_factory,
        parameter_deserializers_factory: ParameterDeserializersFactory = parameter_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
    ):
        self.spec = spec
        self.base_url = base_url

        self.schema_unmarshallers_factory = (
            schema_unmarshallers_factory or self.schema_unmarshallers_factory
        )
        if self.schema_unmarshallers_factory is NotImplemented:
            raise NotImplementedError(
                "schema_unmarshallers_factory is not assigned"
            )

        self.schema_casters_factory = schema_casters_factory
        self.parameter_deserializers_factory = parameter_deserializers_factory
        self.media_type_deserializers_factory = (
            media_type_deserializers_factory
        )

    def _get_media_type(self, content: Spec, mimetype: str) -> MediaType:
        from openapi_core.templating.media_types.finders import MediaTypeFinder

        finder = MediaTypeFinder(content)
        return finder.find(mimetype)

    def _deserialise_data(self, mimetype: str, value: Any) -> Any:
        deserializer = self.media_type_deserializers_factory.create(mimetype)
        return deserializer(value)

    def _deserialise_parameter(self, param: Spec, value: Any) -> Any:
        deserializer = self.parameter_deserializers_factory.create(param)
        return deserializer(value)

    def _cast(self, schema: Spec, value: Any) -> Any:
        caster = self.schema_casters_factory.create(schema)
        return caster(value)

    def _unmarshal(self, schema: Spec, value: Any) -> Any:
        unmarshaller = self.schema_unmarshallers_factory.create(schema)
        return unmarshaller(value)

    def _get_param_or_header_value(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
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


class BaseAPICallValidator(BaseValidator):
    @cached_property
    def path_finder(self) -> BasePathFinder:
        return APICallPathFinder(self.spec, base_url=self.base_url)

    def _find_path(self, request: Request) -> PathOperationServer:
        path_pattern = getattr(request, "path_pattern", None) or request.path
        full_url = urljoin(request.host_url, path_pattern)
        return self.path_finder.find(request.method, full_url)


class BaseWebhookValidator(BaseValidator):
    @cached_property
    def path_finder(self) -> BasePathFinder:
        return WebhookPathFinder(self.spec, base_url=self.base_url)

    def _find_path(self, request: WebhookRequest) -> PathOperationServer:
        return self.path_finder.find(request.method, request.name)
