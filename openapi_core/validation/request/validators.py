"""OpenAPI core validation request validators module"""
from itertools import chain
from six import iteritems

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.schema.media_types.exceptions import (
    InvalidMediaTypeValue, InvalidContentType,
)
from openapi_core.schema.operations.exceptions import InvalidOperation
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
                raw_value = param.get_raw_value(request)
            except MissingRequiredParameter as exc:
                errors.append(exc)
                continue
            except MissingParameter:
                if not param.schema or not param.schema.has_default():
                    continue
                casted = param.schema.default
            else:
                try:
                    deserialised = self._deserialise(param, raw_value)
                except OpenAPIParameterError as exc:
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
            raw_body = operation.request_body.get_value(request)
        except MissingRequestBody as exc:
            return None, [exc, ]

        try:
            deserialised = self._deserialise(media_type, raw_body)
        except InvalidMediaTypeValue as exc:
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

    def _deserialise(self, param_or_media_type, value):
        return param_or_media_type.deserialise(value)

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
