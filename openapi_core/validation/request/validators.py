"""OpenAPI core validation request validators module"""
from itertools import chain
from six import iteritems

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.parameters.enums import ParameterLocation
from openapi_core.schema.parameters.exceptions import (
    OpenAPIParameterError, MissingRequiredParameter, MissingParameter,
)
from openapi_core.schema.paths.exceptions import InvalidPath
from openapi_core.schema.request_bodies.exceptions import MissingRequestBody
from openapi_core.schema.servers.exceptions import InvalidServer
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.validation.request.datatypes import (
    RequestParameters, RequestValidationResult,
)
from openapi_core.validation.util import get_operation_pattern


class RequestValidator(object):

    def __init__(self, spec, custom_formatters=None):
        self.spec = spec
        self.custom_formatters = custom_formatters

    def validate(self, request):
        try:
            path = self._get_path(request)
            operation = self._get_operation(request)
        # don't process if operation errors
        except (InvalidServer, InvalidPath, InvalidOperation) as exc:
            return RequestValidationResult([exc, ], None, None)

        params, params_errors = self._get_parameters(
            request, chain(
                iteritems(operation.parameters),
                iteritems(path.parameters)
            )
        )

        body, body_errors = self._get_body(request, operation)

        errors = params_errors + body_errors
        return RequestValidationResult(errors, body, params)

    def _validate_parameters(self, request):
        try:
            path = self._get_path(request)
            operation = self._get_operation(request)
        except (InvalidServer, InvalidPath, InvalidOperation) as exc:
            return RequestValidationResult([exc, ], None, None)

        params, params_errors = self._get_parameters(
            request, chain(
                iteritems(operation.parameters),
                iteritems(path.parameters)
            )
        )
        return RequestValidationResult(params_errors, None, params)

    def _validate_body(self, request):
        try:
            operation = self._get_operation(request)
        except (InvalidServer, InvalidOperation) as exc:
            return RequestValidationResult([exc, ], None, None)

        body, body_errors = self._get_body(request, operation)
        return RequestValidationResult(body_errors, body, None)

    def _get_operation_pattern(self, request):
        server = self.spec.get_server(request.full_url_pattern)

        return get_operation_pattern(
            server.default_url, request.full_url_pattern
        )

    def _get_path(self, request):
        operation_pattern = self._get_operation_pattern(request)

        return self.spec[operation_pattern]

    def _get_operation(self, request):
        operation_pattern = self._get_operation_pattern(request)

        return self.spec.get_operation(operation_pattern, request.method)

    def _get_parameters(self, request, params):
        errors = []
        seen = set()
        locations = {}
        for param_name, param in params:
            if (param_name, param.location.value) in seen:
                # skip parameter already seen
                # e.g. overriden path item paremeter on operation
                continue
            seen.add((param_name, param.location.value))
            try:
                raw_value = self._get_parameter_value(param, request)
            except MissingRequiredParameter as exc:
                errors.append(exc)
                continue
            except MissingParameter:
                if not param.schema or not param.schema.has_default():
                    continue
                casted = param.schema.default
            else:
                try:
                    deserialised = self._deserialise_parameter(
                        param, raw_value)
                except DeserializeError as exc:
                    errors.append(exc)
                    continue

                try:
                    casted = self._cast(param, deserialised)
                except CastError as exc:
                    errors.append(exc)
                    continue

            try:
                unmarshalled = self._unmarshal(param, casted)
            except (ValidateError, UnmarshalError) as exc:
                errors.append(exc)
            else:
                locations.setdefault(param.location.value, {})
                locations[param.location.value][param_name] = unmarshalled

        return RequestParameters(**locations), errors

    def _get_body(self, request, operation):
        if operation.request_body is None:
            return None, []

        try:
            media_type = operation.request_body[request.mimetype]
        except InvalidContentType as exc:
            return None, [exc, ]

        try:
            raw_body = self._get_body_value(operation.request_body, request)
        except MissingRequestBody as exc:
            return None, [exc, ]

        try:
            deserialised = self._deserialise_media_type(media_type, raw_body)
        except DeserializeError as exc:
            return None, [exc, ]

        try:
            casted = self._cast(media_type, deserialised)
        except CastError as exc:
            return None, [exc, ]

        try:
            body = self._unmarshal(media_type, casted)
        except (ValidateError, UnmarshalError) as exc:
            return None, [exc, ]

        return body, []

    def _get_parameter_value(self, param, request):
        location = request.parameters[param.location.value]

        if param.name not in location:
            if param.required:
                raise MissingRequiredParameter(param.name)

            raise MissingParameter(param.name)

        if param.aslist and param.explode:
            if hasattr(location, 'getall'):
                return location.getall(param.name)
            return location.getlist(param.name)

        return location[param.name]

    def _get_body_value(self, request_body, request):
        if not request.body and request_body.required:
            raise MissingRequestBody(request)
        return request.body

    def _deserialise_media_type(self, media_type, value):
        from openapi_core.deserializing.media_types.factories import (
            MediaTypeDeserializersFactory,
        )
        deserializers_factory = MediaTypeDeserializersFactory()
        deserializer = deserializers_factory.create(media_type)
        return deserializer(value)


    def _deserialise_parameter(self, param, value):
        from openapi_core.deserializing.parameters.factories import (
            ParameterDeserializersFactory,
        )
        deserializers_factory = ParameterDeserializersFactory()
        deserializer = deserializers_factory.create(param)
        return deserializer(value)

    def _cast(self, param_or_media_type, value):
        # return param_or_media_type.cast(value)
        if not param_or_media_type.schema:
            return value

        from openapi_core.casting.schemas.exceptions import CastError
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
            self.spec._resolver, self.custom_formatters)
        unmarshaller = unmarshallers_factory.create(
            param_or_media_type.schema)
        return unmarshaller(value)
