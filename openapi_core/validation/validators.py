"""OpenAPI core validation validators module"""
import re
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
from openapi_core.deserializing.styles import style_deserializers_factory
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest
from openapi_core.schema.parameters import get_aslist
from openapi_core.schema.parameters import get_deep_object_value
from openapi_core.schema.parameters import get_explode
from openapi_core.schema.parameters import get_style
from openapi_core.schema.protocols import SuportsGetAll
from openapi_core.schema.protocols import SuportsGetList
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
        style_deserializers_factory: StyleDeserializersFactory = style_deserializers_factory,
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
        self.style_deserializers_factory = style_deserializers_factory
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

    def _find_media_type(
        self, content: Spec, mimetype: Optional[str] = None
    ) -> MediaType:
        from openapi_core.templating.media_types.finders import MediaTypeFinder

        finder = MediaTypeFinder(content)
        if mimetype is None:
            return finder.get_first()
        return finder.find(mimetype)

    def _deserialise_media_type(
        self, mimetype: str, parameters: Mapping[str, str], value: Any
    ) -> Any:
        deserializer = self.media_type_deserializers_factory.create(
            mimetype,
            extra_media_type_deserializers=self.extra_media_type_deserializers,
            parameters=parameters,
        )
        return deserializer.deserialize(value)

    def _deserialise_style(self, param_or_header: Spec, value: Any) -> Any:
        deserializer = self.style_deserializers_factory.create(param_or_header)
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

    def _get_param_or_header(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        # Simple scenario
        if "content" not in param_or_header:
            return self._get_simple_param_or_header(
                param_or_header, location, name=name
            )

        # Complex scenario
        return self._get_complex_param_or_header(
            param_or_header, location, name=name
        )

    def _get_simple_param_or_header(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        try:
            raw = self._get_style_value(param_or_header, location, name=name)
        except KeyError:
            # in simple scenrios schema always exist
            schema = param_or_header / "schema"
            if "default" not in schema:
                raise
            raw = schema["default"]
        return self._convert_schema_style_value(raw, param_or_header)

    def _get_complex_param_or_header(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        content = param_or_header / "content"
        # no point to catch KetError
        # in complex scenrios schema doesn't exist
        raw = self._get_media_type_value(param_or_header, location, name=name)
        return self._convert_content_schema_value(raw, content)

    def _convert_schema_style_value(
        self,
        raw: Any,
        param_or_header: Spec,
    ) -> Any:
        casted, schema = self._convert_schema_style_value_and_schema(
            raw, param_or_header
        )
        if schema is None:
            return casted
        self._validate_schema(schema, casted)
        return casted

    def _convert_content_schema_value(
        self, raw: Any, content: Spec, mimetype: Optional[str] = None
    ) -> Any:
        casted, schema = self._convert_content_schema_value_and_schema(
            raw, content, mimetype
        )
        if schema is None:
            return casted
        self._validate_schema(schema, casted)
        return casted

    def _convert_schema_style_value_and_schema(
        self,
        raw: Any,
        param_or_header: Spec,
    ) -> Tuple[Any, Spec]:
        deserialised = self._deserialise_style(param_or_header, raw)
        schema = param_or_header / "schema"
        casted = self._cast(schema, deserialised)
        return casted, schema

    def _convert_content_schema_value_and_schema(
        self,
        raw: Any,
        content: Spec,
        mimetype: Optional[str] = None,
    ) -> Tuple[Any, Optional[Spec]]:
        mime_type, parameters, media_type = self._find_media_type(
            content, mimetype
        )
        deserialised = self._deserialise_media_type(mime_type, parameters, raw)
        casted = self._cast(media_type, deserialised)

        if "schema" not in media_type:
            return casted, None

        schema = media_type / "schema"
        return casted, schema

    def _get_style_value(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        name = name or param_or_header["name"]
        style = get_style(param_or_header)
        if name not in location:
            # Only check if the name is not in the location if the style of
            # the param is deepObject,this is because deepObjects will never be found
            # as their key also includes the properties of the object already.
            if style != "deepObject":
                raise KeyError
            keys_str = " ".join(location.keys())
            if not re.search(rf"{name}\[\w+\]", keys_str):
                raise KeyError

        aslist = get_aslist(param_or_header)
        explode = get_explode(param_or_header)
        if aslist and explode:
            if style == "deepObject":
                return get_deep_object_value(location, name)
            if isinstance(location, SuportsGetAll):
                return location.getall(name)
            if isinstance(location, SuportsGetList):
                return location.getlist(name)

        return location[name]

    def _get_media_type_value(
        self,
        param_or_header: Spec,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        name = name or param_or_header["name"]
        return location[name]


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
