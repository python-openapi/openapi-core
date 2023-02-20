from typing import Any
from typing import Mapping
from typing import Optional
from typing import Tuple

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
from openapi_core.spec import Spec
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
            parameter_deserializers_factory=parameter_deserializers_factory,
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

    def _unmarshal_schema(self, schema: Spec, value: Any) -> Any:
        unmarshaller = self.schema_unmarshallers_factory.create(
            schema,
            format_validators=self.format_validators,
            extra_format_validators=self.extra_format_validators,
            format_unmarshallers=self.format_unmarshallers,
            extra_format_unmarshallers=self.extra_format_unmarshallers,
        )
        return unmarshaller.unmarshal(value)

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
        return self._unmarshal_schema(schema, casted)

    def _get_content_value(
        self, raw: Any, mimetype: str, content: Spec
    ) -> Any:
        casted, schema = self._get_content_value_and_schema(
            raw, mimetype, content
        )
        if schema is None:
            return casted
        return self._unmarshal_schema(schema, casted)
