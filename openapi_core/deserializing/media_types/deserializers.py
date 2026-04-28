from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Optional
from xml.etree.ElementTree import ParseError

from jsonschema_path import SchemaPath

from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types.datatypes import (
    DeserializerCallable,
)
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.exceptions import (
    MediaTypeDeserializeError,
)
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.schema.encodings import get_content_type
from openapi_core.schema.parameters import get_style_and_explode
from openapi_core.schema.protocols import SuportsGetAll
from openapi_core.schema.protocols import SuportsGetList
from openapi_core.schema.schemas import get_properties
from openapi_core.validation.schemas.exceptions import ValidateError
from openapi_core.validation.schemas.validators import SchemaValidator

if TYPE_CHECKING:
    from openapi_core.casting.schemas.casters import SchemaCaster


class MediaTypesDeserializer:
    def __init__(
        self,
        media_type_deserializers: Optional[MediaTypeDeserializersDict] = None,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
    ):
        if media_type_deserializers is None:
            media_type_deserializers = {}
        self.media_type_deserializers = media_type_deserializers
        if extra_media_type_deserializers is None:
            extra_media_type_deserializers = {}
        self.extra_media_type_deserializers = extra_media_type_deserializers

    def deserialize(
        self, mimetype: str, value: bytes, **parameters: str
    ) -> Any:
        deserializer_callable = self.get_deserializer_callable(mimetype)

        try:
            return deserializer_callable(value, **parameters)
        except (ParseError, ValueError, TypeError, AttributeError):
            raise MediaTypeDeserializeError(mimetype, value)

    def get_deserializer_callable(
        self,
        mimetype: str,
    ) -> DeserializerCallable:
        if mimetype in self.extra_media_type_deserializers:
            return self.extra_media_type_deserializers[mimetype]
        return self.media_type_deserializers[mimetype]


@dataclass(frozen=True)
class FormMediaSchemaMatch:
    schema: SchemaPath
    decoded_candidate: Mapping[str, Any]


class MediaTypeDeserializer:
    def __init__(
        self,
        spec: SchemaPath,
        style_deserializers_factory: StyleDeserializersFactory,
        media_types_deserializer: MediaTypesDeserializer,
        mimetype: str,
        schema: Optional[SchemaPath] = None,
        schema_validator: Optional[SchemaValidator] = None,
        schema_caster: Optional["SchemaCaster"] = None,
        encoding: Optional[SchemaPath] = None,
        **parameters: str,
    ):
        self.spec = spec
        self.style_deserializers_factory = style_deserializers_factory
        self.media_types_deserializer = media_types_deserializer
        self.mimetype = mimetype
        self.schema = schema
        self.schema_validator = schema_validator
        self.schema_caster = schema_caster
        self.encoding = encoding
        self.parameters = parameters

    def deserialize(self, value: bytes) -> Any:
        deserialized = self.media_types_deserializer.deserialize(
            self.mimetype, value, **self.parameters
        )

        if (
            self.mimetype != "application/x-www-form-urlencoded"
            and not self.mimetype.startswith("multipart")
        ):
            return deserialized

        # Decode form-media bodies only when a schema is available.
        if self.schema is not None:
            return self.decode(deserialized)

        return deserialized

    def evolve(
        self,
        schema: SchemaPath,
        mimetype: Optional[str] = None,
    ) -> "MediaTypeDeserializer":
        cls = self.__class__

        schema_validator = None
        if self.schema_validator is not None:
            schema_validator = self.schema_validator.evolve(schema)

        schema_caster = None
        if self.schema_caster is not None:
            schema_caster = self.schema_caster.evolve(schema)

        return cls(
            self.spec,
            self.style_deserializers_factory,
            self.media_types_deserializer,
            mimetype=mimetype or self.mimetype,
            schema=schema,
            schema_validator=schema_validator,
            schema_caster=schema_caster,
            encoding=self.encoding,
            **self.parameters,
        )

    def decode(
        self,
        location: Mapping[str, Any],
        schema_only: bool = False,
        use_defaults: bool = True,
    ) -> Mapping[str, Any]:
        # Form-media decoding always needs a schema to resolve properties.
        assert self.schema is not None
        properties: dict[str, Any] = {}

        # For form media, select composed branches from decoded candidates.
        if self.schema_validator is not None:
            one_of_match = self.get_form_media_one_of_match(location)
            if one_of_match is not None:
                self.update_decoded_properties(
                    properties,
                    one_of_match.decoded_candidate,
                )

            any_of_matches = self.iter_form_media_any_of_matches(location)
            for any_of_match in any_of_matches:
                self.update_decoded_properties(
                    properties,
                    any_of_match.decoded_candidate,
                )

            all_of_matches = self.iter_form_media_all_of_matches(location)
            for all_of_match in all_of_matches:
                self.update_decoded_properties(
                    properties,
                    all_of_match.decoded_candidate,
                )

        for prop_name, prop_schema in get_properties(self.schema).items():
            try:
                properties[prop_name] = self.decode_property(
                    prop_name, prop_schema, location
                )
            except KeyError:
                if not use_defaults or "default" not in prop_schema:
                    continue
                properties[prop_name] = (prop_schema / "default").read_value()

        if schema_only:
            return properties

        return properties

    def update_decoded_properties(
        self,
        properties: dict[str, Any],
        candidate: Mapping[str, Any],
    ) -> None:
        for prop_name, prop_value in candidate.items():
            if prop_name not in properties:
                properties[prop_name] = prop_value
                continue

            properties[prop_name] = self.merge_decoded_property_value(
                properties[prop_name],
                prop_value,
            )

    def merge_decoded_property_value(self, current: Any, new: Any) -> Any:
        if current == new:
            return current

        # Prefer lossless binary values over surrogate-decoded text when
        # overlapping composed branches describe the same multipart field.
        if isinstance(current, bytes) and isinstance(new, str):
            return current
        if isinstance(current, str) and isinstance(new, bytes):
            return new

        return new

    def get_form_media_one_of_match(
        self,
        location: Mapping[str, Any],
    ) -> Optional[FormMediaSchemaMatch]:
        if self.schema is None or "oneOf" not in self.schema:
            return None

        for subschema in self.schema / "oneOf":
            match = self.get_form_media_schema_match(subschema, location)
            if match is not None:
                return match

        return None

    def iter_form_media_any_of_matches(
        self,
        location: Mapping[str, Any],
    ) -> list[FormMediaSchemaMatch]:
        if self.schema is None or "anyOf" not in self.schema:
            return []

        return list(self.iter_form_media_schema_matches("anyOf", location))

    def iter_form_media_all_of_matches(
        self,
        location: Mapping[str, Any],
    ) -> list[FormMediaSchemaMatch]:
        if self.schema is None or "allOf" not in self.schema:
            return []

        return list(self.iter_form_media_schema_matches("allOf", location))

    def iter_form_media_schema_matches(
        self,
        keyword: str,
        location: Mapping[str, Any],
    ) -> Iterator[FormMediaSchemaMatch]:
        assert self.schema is not None

        for subschema in self.schema / keyword:
            match = self.get_form_media_schema_match(subschema, location)
            if match is not None:
                yield match

    def get_form_media_schema_match(
        self,
        subschema: SchemaPath,
        location: Mapping[str, Any],
    ) -> Optional[FormMediaSchemaMatch]:
        assert self.schema_validator is not None

        deserializer = self.evolve(subschema)
        try:
            validation_decoded_candidate = deserializer.decode(
                location,
                schema_only=True,
                use_defaults=False,
            )
        except DeserializeError:
            return None

        validator = self.schema_validator.evolve(subschema)
        validation_candidate = dict(location)
        validation_candidate.update(validation_decoded_candidate)

        try:
            validator.validate(validation_candidate)
        except ValidateError:
            return None

        decoded_candidate = deserializer.decode(location, schema_only=True)

        return FormMediaSchemaMatch(subschema, decoded_candidate)

    def decode_property(
        self,
        prop_name: str,
        prop_schema: SchemaPath,
        location: Mapping[str, Any],
    ) -> Any:
        if self.encoding is None or prop_name not in self.encoding:
            if self.mimetype == "application/x-www-form-urlencoded":
                # default serialization strategy for complex objects
                # in the application/x-www-form-urlencoded
                return self.decode_property_style(
                    prop_name,
                    prop_schema,
                    location,
                    SchemaPath.from_dict({"style": "form"}),
                )
            return self.decode_property_content_type(
                prop_name, prop_schema, location
            )

        prep_encoding = self.encoding / prop_name
        if (
            "style" not in prep_encoding
            and "explode" not in prep_encoding
            and "allowReserved" not in prep_encoding
        ):
            return self.decode_property_content_type(
                prop_name, prop_schema, location, prep_encoding
            )

        return self.decode_property_style(
            prop_name, prop_schema, location, prep_encoding
        )

    def decode_property_style(
        self,
        prop_name: str,
        prop_schema: SchemaPath,
        location: Mapping[str, Any],
        prep_encoding: SchemaPath,
    ) -> Any:
        prop_style, prop_explode = get_style_and_explode(
            prep_encoding, default_location="query"
        )
        prop_deserializer = self.style_deserializers_factory.create(
            self.spec, prop_schema, prop_style, prop_explode, name=prop_name
        )
        return prop_deserializer.deserialize(location)

    def decode_property_content_type(
        self,
        prop_name: str,
        prop_schema: SchemaPath,
        location: Mapping[str, Any],
        prop_encoding: Optional[SchemaPath] = None,
    ) -> Any:
        prop_content_type = get_content_type(prop_schema, prop_encoding)
        prop_deserializer = self.evolve(
            prop_schema,
            mimetype=prop_content_type,
        )
        prop_schema_type = (prop_schema / "type").read_str("")
        if (
            self.mimetype.startswith("multipart")
            and prop_schema_type == "array"
        ):
            if isinstance(location, SuportsGetAll):
                value = location.getall(prop_name)
                return list(map(prop_deserializer.deserialize, value))
            if isinstance(location, SuportsGetList):
                value = location.getlist(prop_name)
                return list(map(prop_deserializer.deserialize, value))

        return prop_deserializer.deserialize(location[prop_name])
