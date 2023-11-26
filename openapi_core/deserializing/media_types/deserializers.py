from typing import Any
from typing import Mapping
from typing import Optional
from xml.etree.ElementTree import ParseError

from jsonschema_path import SchemaPath

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


class MediaTypeDeserializer:
    def __init__(
        self,
        style_deserializers_factory: StyleDeserializersFactory,
        media_types_deserializer: MediaTypesDeserializer,
        mimetype: str,
        schema: Optional[SchemaPath] = None,
        encoding: Optional[SchemaPath] = None,
        **parameters: str,
    ):
        self.style_deserializers_factory = style_deserializers_factory
        self.media_types_deserializer = media_types_deserializer
        self.mimetype = mimetype
        self.schema = schema
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

        # decode multipart request bodies
        return self.decode(deserialized)

    def evolve(
        self, mimetype: str, schema: Optional[SchemaPath]
    ) -> "MediaTypeDeserializer":
        cls = self.__class__

        return cls(
            self.style_deserializers_factory,
            self.media_types_deserializer,
            mimetype,
            schema=schema,
        )

    def decode(self, location: Mapping[str, Any]) -> Mapping[str, Any]:
        # schema is required for multipart
        assert self.schema is not None
        properties = {}
        for prop_name, prop_schema in get_properties(self.schema).items():
            try:
                properties[prop_name] = self.decode_property(
                    prop_name, prop_schema, location
                )
            except KeyError:
                if "default" not in prop_schema:
                    continue
                properties[prop_name] = prop_schema["default"]

        return properties

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
            prop_style, prop_explode, prop_schema, name=prop_name
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
            prop_content_type,
            prop_schema,
        )
        prop_schema_type = prop_schema.getkey("type", "")
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
