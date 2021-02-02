"""OpenAPI core validation request validators module"""
from itertools import chain
from six import iteritems

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.schema.media_types.exceptions import InvalidContentType
from openapi_core.schema.parameters.exceptions import (
    MissingRequiredParameter, MissingParameter,
)
from openapi_core.schema.request_bodies.exceptions import MissingRequestBody
from openapi_core.security.exceptions import SecurityError
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.request.datatypes import (
    RequestParameters, RequestValidationResult,
)
from openapi_core.validation.validators import BaseValidator


class RequestValidator(BaseValidator):

    def validate(self, request):
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestValidationResult(errors=[exc, ])

        try:
            security = self._get_security(request, operation)
        except InvalidSecurity as exc:
            return RequestValidationResult(errors=[exc, ])

        request.parameters.path = request.parameters.path or \
            path_result.variables
        params, params_errors = self._get_parameters(
            request, chain(
                iteritems(operation.parameters),
                iteritems(path.parameters)
            )
        )

        body, body_errors = self._get_body(request, operation)

        errors = params_errors + body_errors
        return RequestValidationResult(
            errors=errors,
            body=body,
            parameters=params,
            security=security,
        )

    def _validate_parameters(self, request):
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc, ])

        request.parameters.path = request.parameters.path or \
            path_result.variables
        params, params_errors = self._get_parameters(
            request, chain(
                iteritems(operation.parameters),
                iteritems(path.parameters)
            )
        )
        return RequestValidationResult(
            errors=params_errors,
            parameters=params,
        )

    def _validate_body(self, request):
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc, ])

        body, body_errors = self._get_body(request, operation)
        return RequestValidationResult(
            errors=body_errors,
            body=body,
        )

    def _get_security(self, request, operation):
        security = self.spec.security
        if operation.security is not None:
            security = operation.security

        if not security:
            return {}

        for security_requirement in security:
            try:
                return {
                    scheme_name: self._get_security_value(
                        scheme_name, request)
                    for scheme_name in security_requirement
                }
            except SecurityError:
                continue

        raise InvalidSecurity()

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

    def _get_security_value(self, scheme_name, request):
        scheme = self.spec.components.security_schemes.get(scheme_name)
        if not scheme:
            return

        from openapi_core.security.factories import SecurityProviderFactory
        security_provider_factory = SecurityProviderFactory()
        security_provider = security_provider_factory.create(scheme)
        return security_provider(request)

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

    def _deserialise_parameter(self, param, value):
        from openapi_core.deserializing.parameters.factories import (
            ParameterDeserializersFactory,
        )
        deserializers_factory = ParameterDeserializersFactory()
        deserializer = deserializers_factory.create(param)
        return deserializer(value)

    def _unmarshal(self, param_or_media_type, value):
        return super(RequestValidator, self)._unmarshal(
            param_or_media_type, value, context=UnmarshalContext.REQUEST,
        )
