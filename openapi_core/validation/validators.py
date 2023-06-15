"""OpenAPI core validation validators module"""
from functools import cached_property
from typing import Any
from typing import Mapping
from typing import Optional
from typing import Tuple
from urllib.parse import urljoin

from openapi_core.casting.schemas import schema_casters_factory
from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types import (
    media_type_deserializers_factory,
)
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
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
from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest
from openapi_core.schema.parameters import get_value
from openapi_core.spec import Spec
from openapi_core.templating.media_types.datatypes import MediaType
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.finders import APICallPathFinder
from openapi_core.templating.paths.finders import BasePathFinder
from openapi_core.templating.paths.finders import WebhookPathFinder
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory


class BaseValidator:
    schema_validators_factory: SchemaValidatorsFactory = NotImplemented

    def __init__(
        self,
        spec: Spec,
        base_url: Optional[str] = None,
        schema_casters_factory: SchemaCastersFactory = schema_casters_factory,
        parameter_deserializers_factory: ParameterDeserializersFactory = parameter_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
        schema_validators_factory: Optional[SchemaValidatorsFactory] = None,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
    ):
        self.spec = spec
        self.base_url = base_url

        self.schema_casters_factory = schema_casters_factory
        self.parameter_deserializers_factory = parameter_deserializers_factory
        self.media_type_deserializers_factory = (
            media_type_deserializers_factory
        )
        self.schema_validators_factory = (
            schema_validators_factory or self.schema_validators_factory
        )
        if self.schema_validators_factory is NotImplemented:
            raise NotImplementedError(
                "schema_validators_factory is not assigned"
            )
        self.format_validators = format_validators
        self.extra_format_validators = extra_format_validators
        self.extra_media_type_deserializers = extra_media_type_deserializers

    def _get_media_type(self, content: Spec, mimetype: str) -> MediaType:
        from openapi_core.templating.media_types.finders import MediaTypeFinder

        finder = MediaTypeFinder(content)
        return finder.find(mimetype)

    def _deserialise_data(self, mimetype: str, value: Any) -> Any:
        deserializer = self.media_type_deserializers_factory.create(
            mimetype,
            extra_media_type_deserializers=self.extra_media_type_deserializers,
        )
        return deserializer.deserialize(value)

    def _deserialise_parameter(self, param: Spec, value: Any) -> Any:
        deserializer = self.parameter_deserializers_factory.create(param)
        return deserializer.deserialize(value)

    def _cast(self, schema: Spec, value: Any) -> Any:
        caster = self.schema_casters_factory.create(schema)
        return caster(value)

    def _validate_schema(self, schema: Spec, value: Any) -> None:
        validator = self.schema_validators_factory.create(
            schema,
            format_validators=self.format_validators,
            extra_format_validators=self.extra_format_validators,
        )
        validator.validate(value)

    def _get_param_or_header_value(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        casted, schema = self._get_param_or_header_value_and_schema(
            param_or_header, location, name
        )
        if schema is None:
            return casted
        self._validate_schema(schema, casted)
        return casted

    def _get_content_value(
        self, raw: Any, mimetype: str, content: Spec
    ) -> Any:
        casted, schema = self._get_content_value_and_schema(
            raw, mimetype, content
        )
        if schema is None:
            return casted
        self._validate_schema(schema, casted)
        return casted

    def _get_param_or_header_value_and_schema(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Tuple[Any, Spec]:
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
        return casted, schema

    def _get_content_value_and_schema(
        self, raw: Any, mimetype: str, content: Spec
    ) -> Tuple[Any, Optional[Spec]]:
        media_type, mimetype = self._get_media_type(content, mimetype)
        deserialised = self._deserialise_data(mimetype, raw)
        casted = self._cast(media_type, deserialised)

        if "schema" not in media_type:
            return casted, None

        schema = media_type / "schema"
        return casted, schema


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
