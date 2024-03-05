from typing import Any
from typing import Mapping
from typing import Optional
from typing import Tuple

from jsonschema_path import SchemaPath
from openapi_spec_validator.validation.types import SpecValidatorType

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
from openapi_core.templating.paths.types import PathFinderType
from openapi_core.unmarshalling.schemas.datatypes import (
    FormatUnmarshallersDict,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory
from openapi_core.validation.validators import BaseValidator


class BaseUnmarshaller(BaseValidator):
    schema_unmarshallers_factory: SchemaUnmarshallersFactory = NotImplemented

    def __init__(
        self,
        spec: SchemaPath,
        base_url: Optional[str] = None,
        style_deserializers_factory: StyleDeserializersFactory = style_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
        schema_casters_factory: Optional[SchemaCastersFactory] = None,
        schema_validators_factory: Optional[SchemaValidatorsFactory] = None,
        path_finder_cls: Optional[PathFinderType] = None,
        spec_validator_cls: Optional[SpecValidatorType] = None,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
        schema_unmarshallers_factory: Optional[
            SchemaUnmarshallersFactory
        ] = None,
        format_unmarshallers: Optional[FormatUnmarshallersDict] = None,
        extra_format_unmarshallers: Optional[FormatUnmarshallersDict] = None,
    ):
        if schema_validators_factory is None and schema_unmarshallers_factory:
            schema_validators_factory = (
                schema_unmarshallers_factory.schema_validators_factory
            )
        BaseValidator.__init__(
            self,
            spec,
            base_url=base_url,
            style_deserializers_factory=style_deserializers_factory,
            media_type_deserializers_factory=media_type_deserializers_factory,
            schema_casters_factory=schema_casters_factory,
            schema_validators_factory=schema_validators_factory,
            path_finder_cls=path_finder_cls,
            spec_validator_cls=spec_validator_cls,
            format_validators=format_validators,
            extra_format_validators=extra_format_validators,
            extra_media_type_deserializers=extra_media_type_deserializers,
        )
        self.schema_unmarshallers_factory = (
            schema_unmarshallers_factory or self.schema_unmarshallers_factory
        )
        if self.schema_unmarshallers_factory is NotImplemented:
            raise NotImplementedError(
                "schema_unmarshallers_factory is not assigned"
            )
        self.format_unmarshallers = format_unmarshallers
        self.extra_format_unmarshallers = extra_format_unmarshallers

    def _unmarshal_schema(self, schema: SchemaPath, value: Any) -> Any:
        unmarshaller = self.schema_unmarshallers_factory.create(
            schema,
            format_validators=self.format_validators,
            extra_format_validators=self.extra_format_validators,
            format_unmarshallers=self.format_unmarshallers,
            extra_format_unmarshallers=self.extra_format_unmarshallers,
        )
        return unmarshaller.unmarshal(value)

    def _get_param_or_header_and_schema(
        self,
        param_or_header: SchemaPath,
        location: Mapping[str, Any],
        name: Optional[str] = None,
    ) -> Tuple[Any, Optional[SchemaPath]]:
        casted, schema = super()._get_param_or_header_and_schema(
            param_or_header, location, name=name
        )
        if schema is None:
            return casted, None
        return self._unmarshal_schema(schema, casted), schema

    def _get_content_and_schema(
        self, raw: Any, content: SchemaPath, mimetype: Optional[str] = None
    ) -> Tuple[Any, Optional[SchemaPath]]:
        casted, schema = super()._get_content_and_schema(
            raw, content, mimetype
        )
        if schema is None:
            return casted, None
        return self._unmarshal_schema(schema, casted), schema
