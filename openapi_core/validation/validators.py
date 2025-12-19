"""OpenAPI core validation validators module"""

import warnings
from functools import cached_property
from typing import Any
from typing import Mapping
from typing import Optional
from typing import Tuple
from urllib.parse import urljoin

from jsonschema_path import SchemaPath
from openapi_spec_validator.validation.types import SpecValidatorType

from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types import media_type_deserializers
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.styles import style_deserializers
from openapi_core.deserializing.styles.exceptions import (
    EmptyQueryParameterValue,
)
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest
from openapi_core.schema.parameters import get_style_and_explode
from openapi_core.templating.media_types.datatypes import MediaType
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.finders import APICallPathFinder
from openapi_core.templating.paths.finders import BasePathFinder
from openapi_core.templating.paths.finders import WebhookPathFinder
from openapi_core.templating.paths.types import PathFinderType
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory


class BaseValidator:
    schema_casters_factory: SchemaCastersFactory = NotImplemented
    schema_validators_factory: SchemaValidatorsFactory = NotImplemented
    path_finder_cls: PathFinderType = NotImplemented
    spec_validator_cls: Optional[SpecValidatorType] = None

    def __init__(
        self,
        spec: SchemaPath,
        base_url: Optional[str] = None,
        style_deserializers_factory: Optional[
            StyleDeserializersFactory
        ] = None,
        media_type_deserializers_factory: Optional[
            MediaTypeDeserializersFactory
        ] = None,
        schema_casters_factory: Optional[SchemaCastersFactory] = None,
        schema_validators_factory: Optional[SchemaValidatorsFactory] = None,
        path_finder_cls: Optional[PathFinderType] = None,
        spec_validator_cls: Optional[SpecValidatorType] = None,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
    ):
        self.spec = spec
        self.base_url = base_url

        self.schema_casters_factory = (
            schema_casters_factory or self.schema_casters_factory
        )
        if self.schema_casters_factory is NotImplemented:
            raise NotImplementedError("schema_casters_factory is not assigned")
        self.style_deserializers_factory = (
            style_deserializers_factory
            or StyleDeserializersFactory(
                self.schema_casters_factory,
                style_deserializers=style_deserializers,
            )
        )
        self.media_type_deserializers_factory = (
            media_type_deserializers_factory
            or MediaTypeDeserializersFactory(
                self.style_deserializers_factory,
                media_type_deserializers=media_type_deserializers,
            )
        )
        self.schema_validators_factory = (
            schema_validators_factory or self.schema_validators_factory
        )
        if self.schema_validators_factory is NotImplemented:
            raise NotImplementedError(
                "schema_validators_factory is not assigned"
            )
        self.path_finder_cls = path_finder_cls or self.path_finder_cls
        if self.path_finder_cls is NotImplemented:
            raise NotImplementedError("path_finder_cls is not assigned")
        self.spec_validator_cls = spec_validator_cls or self.spec_validator_cls
        self.format_validators = format_validators
        self.extra_format_validators = extra_format_validators
        self.extra_media_type_deserializers = extra_media_type_deserializers

    @cached_property
    def path_finder(self) -> BasePathFinder:
        return self.path_finder_cls(self.spec, base_url=self.base_url)

    def check_spec(self, spec: SchemaPath) -> None:
        if self.spec_validator_cls is None:
            return

        validator = self.spec_validator_cls(spec)
        validator.validate()

    def _find_media_type(
        self, content: SchemaPath, mimetype: Optional[str] = None
    ) -> MediaType:
        from openapi_core.templating.media_types.finders import MediaTypeFinder

        finder = MediaTypeFinder(content)
        if mimetype is None:
            return finder.get_first()
        return finder.find(mimetype)

    def _deserialise_media_type(
        self,
        media_type: SchemaPath,
        mimetype: str,
        parameters: Mapping[str, str],
        value: bytes,
    ) -> Any:
        schema = media_type.get("schema")
        encoding = None
        if "encoding" in media_type:
            encoding = media_type.get("encoding")
        schema_validator = None
        if schema is not None:
            schema_validator = self.schema_validators_factory.create(
                schema,
                format_validators=self.format_validators,
                extra_format_validators=self.extra_format_validators,
            )
        deserializer = self.media_type_deserializers_factory.create(
            mimetype,
            schema=schema,
            schema_validator=schema_validator,
            parameters=parameters,
            encoding=encoding,
            extra_media_type_deserializers=self.extra_media_type_deserializers,
        )
        return deserializer.deserialize(value)

    def _deserialise_style(
        self,
        param_or_header: SchemaPath,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        name = name or param_or_header["name"]
        style, explode = get_style_and_explode(param_or_header)
        schema = param_or_header / "schema"
        deserializer = self.style_deserializers_factory.create(
            style, explode, schema, name=name
        )
        return deserializer.deserialize(location)

    def _validate_schema(self, schema: SchemaPath, value: Any) -> None:
        validator = self.schema_validators_factory.create(
            schema,
            format_validators=self.format_validators,
            extra_format_validators=self.extra_format_validators,
        )
        validator.validate(value)

    def _get_param_or_header_and_schema(
        self,
        param_or_header: SchemaPath,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Tuple[Any, Optional[SchemaPath]]:
        schema: Optional[SchemaPath] = None
        # Simple scenario
        if "content" not in param_or_header:
            casted, schema = self._get_simple_param_or_header(
                param_or_header, location, name=name
            )
        # Complex scenario
        else:
            casted, schema = self._get_complex_param_or_header(
                param_or_header, location, name=name
            )

        if schema is None:
            return casted, None
        self._validate_schema(schema, casted)
        return casted, schema

    def _get_simple_param_or_header(
        self,
        param_or_header: SchemaPath,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Tuple[Any, SchemaPath]:
        allow_empty_values = param_or_header.getkey("allowEmptyValue")
        if allow_empty_values:
            warnings.warn(
                "Use of allowEmptyValue property is deprecated",
                DeprecationWarning,
            )
        # in simple scenrios schema always exist
        schema = param_or_header / "schema"
        try:
            deserialised = self._deserialise_style(
                param_or_header, location, name=name
            )
        except KeyError:
            if "default" not in schema:
                raise
            return schema["default"], schema
        if allow_empty_values is not None:
            warnings.warn(
                "Use of allowEmptyValue property is deprecated",
                DeprecationWarning,
            )
        if allow_empty_values is None or not allow_empty_values:
            # if "in" not defined then it's a Header
            location_name = param_or_header.getkey("in", "header")
            if (
                location_name == "query"
                and deserialised == ""
                and not allow_empty_values
            ):
                param_or_header_name = param_or_header["name"]
                raise EmptyQueryParameterValue(param_or_header_name)
        return deserialised, schema

    def _get_complex_param_or_header(
        self,
        param_or_header: SchemaPath,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Tuple[Any, Optional[SchemaPath]]:
        content = param_or_header / "content"
        raw = self._get_media_type_value(param_or_header, location, name=name)
        return self._get_content_schema_value_and_schema(raw, content)

    def _get_content_schema_value_and_schema(
        self,
        raw: bytes,
        content: SchemaPath,
        mimetype: Optional[str] = None,
    ) -> Tuple[Any, Optional[SchemaPath]]:
        mime_type, parameters, media_type = self._find_media_type(
            content, mimetype
        )
        # no point to catch KetError
        # in complex scenrios schema doesn't exist
        deserialised = self._deserialise_media_type(
            media_type, mime_type, parameters, raw
        )

        if "schema" not in media_type:
            return deserialised, None

        schema = media_type / "schema"
        return deserialised, schema

    def _get_content_and_schema(
        self, raw: bytes, content: SchemaPath, mimetype: Optional[str] = None
    ) -> Tuple[Any, Optional[SchemaPath]]:
        deserialised, schema = self._get_content_schema_value_and_schema(
            raw, content, mimetype
        )
        if schema is None:
            return deserialised, None
        self._validate_schema(schema, deserialised)
        return deserialised, schema

    def _get_media_type_value(
        self,
        param_or_header: SchemaPath,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Any:
        name = name or param_or_header["name"]
        return location[name]


class BaseAPICallValidator(BaseValidator):
    path_finder_cls = APICallPathFinder

    def _find_path(self, request: Request) -> PathOperationServer:
        path_pattern = getattr(request, "path_pattern", None) or request.path
        full_url = urljoin(request.host_url, path_pattern)
        return self.path_finder.find(request.method, full_url)


class BaseWebhookValidator(BaseValidator):
    path_finder_cls = WebhookPathFinder

    def _find_path(self, request: WebhookRequest) -> PathOperationServer:
        return self.path_finder.find(request.method, request.name)
