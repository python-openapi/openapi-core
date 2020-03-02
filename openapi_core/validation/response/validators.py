"""OpenAPI core validation response validators module"""
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.schema.responses.exceptions import (
    InvalidResponse, MissingResponseContent,
)
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.util import get_operation_pattern


class ResponseValidator(object):

    def __init__(
            self, spec,
            custom_formatters=None, custom_media_type_deserializers=None,
    ):
        self.spec = spec
        self.custom_formatters = custom_formatters
        self.custom_media_type_deserializers = custom_media_type_deserializers

    def validate(self, request, response):
        try:
            operation_response = self._get_operation_response(
                request, response)
        # don't process if operation errors
        except (InvalidServer, InvalidOperation, InvalidResponse) as exc:
            return ResponseValidationResult([exc, ], None, None)

        data, data_errors = self._get_data(response, operation_response)

        headers, headers_errors = self._get_headers(
            response, operation_response)

        errors = data_errors + headers_errors
        return ResponseValidationResult(errors, data, headers)

    def _get_operation_pattern(self, request):
        server = self.spec.get_server(request.full_url_pattern)

        return get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

    def _get_operation(self, request):
        operation_pattern = self._get_operation_pattern(request)

        return self.spec.get_operation(operation_pattern, request.method)

    def _get_operation_response(self, request, response):
        operation = self._get_operation(request)

        return operation.get_response(str(response.status_code))

    def _validate_data(self, request, response):
        try:
            operation_response = self._get_operation_response(
                request, response)
        except (InvalidServer, InvalidOperation, InvalidResponse) as exc:
            return ResponseValidationResult([exc, ], None, None)

        data, data_errors = self._get_data(response, operation_response)
        return ResponseValidationResult(data_errors, data, None)

    def _get_data(self, response, operation_response):
        if not operation_response.content:
            return None, []

        try:
            media_type = operation_response[response.mimetype]
        except InvalidContentType as exc:
            return None, [exc, ]

        try:
            raw_data = self._get_data_value(response)
        except MissingResponseContent as exc:
            return None, [exc, ]

        try:
            deserialised = self._deserialise_media_type(media_type, raw_data)
        except DeserializeError as exc:
            return None, [exc, ]

        try:
            casted = self._cast(media_type, deserialised)
        except CastError as exc:
            return None, [exc, ]

        try:
            data = self._unmarshal(media_type, casted)
        except (ValidateError, UnmarshalError) as exc:
            return None, [exc, ]

        return data, []

    def _get_headers(self, response, operation_response):
        errors = []

        # @todo: implement
        headers = {}

        return headers, errors

    def _get_data_value(self, response):
        if not response.data:
            raise MissingResponseContent(response)

        return response.data

    def _deserialise_media_type(self, media_type, value):
        from openapi_core.deserializing.media_types.factories import (
            MediaTypeDeserializersFactory,
        )
        deserializers_factory = MediaTypeDeserializersFactory(
            self.custom_media_type_deserializers)
        deserializer = deserializers_factory.create(media_type)
        return deserializer(value)

    def _cast(self, param_or_media_type, value):
        # return param_or_media_type.cast(value)
        if not param_or_media_type.schema:
            return value

        from openapi_core.casting.schemas.factories import SchemaCastersFactory
        casters_factory = SchemaCastersFactory()
        caster = casters_factory.create(param_or_media_type.schema)
        return caster(value)

    def _unmarshal(self, param_or_media_type, value):
        if not param_or_media_type.schema:
            return value

        from openapi_core.unmarshalling.schemas.factories import (
            SchemaUnmarshallersFactory,
        )
        unmarshallers_factory = SchemaUnmarshallersFactory(
            self.spec._resolver, self.custom_formatters,
            context=UnmarshalContext.RESPONSE,
        )
        unmarshaller = unmarshallers_factory.create(
            param_or_media_type.schema)
        return unmarshaller(value)
