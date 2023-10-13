from typing import Any
from typing import Mapping
from typing import Optional
from typing import Tuple

from jsonschema_path import SchemaPath

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
        schema_casters_factory: SchemaCastersFactory = schema_casters_factory,
        style_deserializers_factory: StyleDeserializersFactory = style_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
        schema_validators_factory: Optional[SchemaValidatorsFactory] = None,
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
        super().__init__(
            spec,
            base_url=base_url,
            schema_casters_factory=schema_casters_factory,
            style_deserializers_factory=style_deserializers_factory,
            media_type_deserializers_factory=media_type_deserializers_factory,
            schema_validators_factory=schema_validators_factory,
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

    def _convert_schema_style_value(
        self,
        raw: Any,
        param_or_header: SchemaPath,
    ) -> Any:
        casted, schema = self._convert_schema_style_value_and_schema(
            raw, param_or_header
        )
        if schema is None:
            return casted
        return self._unmarshal_schema(schema, casted)

    def _convert_content_schema_value(
        self, raw: Any, content: SchemaPath, mimetype: Optional[str] = None
    ) -> Any:
        casted, schema = self._convert_content_schema_value_and_schema(
            raw, content, mimetype
        )
        if schema is None:
            return casted
        return self._unmarshal_schema(schema, casted)
