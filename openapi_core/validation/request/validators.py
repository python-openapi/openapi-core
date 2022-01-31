"""OpenAPI core validation request validators module"""
import warnings

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.exceptions import MissingParameter
from openapi_core.exceptions import MissingRequestBody
from openapi_core.exceptions import MissingRequiredParameter
from openapi_core.exceptions import MissingRequiredRequestBody
from openapi_core.schema.parameters import iter_params
from openapi_core.security.exceptions import SecurityError
from openapi_core.security.factories import SecurityProviderFactory
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.validators import BaseValidator


class BaseRequestValidator(BaseValidator):
    @property
    def schema_unmarshallers_factory(self):
        spec_resolver = (
            self.spec.accessor.dereferencer.resolver_manager.resolver
        )
        return SchemaUnmarshallersFactory(
            spec_resolver,
            self.format_checker,
            self.custom_formatters,
            context=UnmarshalContext.REQUEST,
        )

    @property
    def security_provider_factory(self):
        return SecurityProviderFactory()

    def _get_parameters(self, request, path, operation):
        operation_params = operation.get("parameters", [])
        path_params = path.get("parameters", [])

        errors = []
        seen = set()
        parameters = Parameters()
        params_iter = iter_params(operation_params, path_params)
        for param in params_iter:
            param_name = param["name"]
            param_location = param["in"]
            if (param_name, param_location) in seen:
                # skip parameter already seen
                # e.g. overriden path item paremeter on operation
                continue
            seen.add((param_name, param_location))
            try:
                value = self._get_parameter(param, request)
            except MissingParameter:
                continue
            except (
                MissingRequiredParameter,
                DeserializeError,
                CastError,
                ValidateError,
                UnmarshalError,
            ) as exc:
                errors.append(exc)
                continue
            else:
                location = getattr(parameters, param_location)
                location[param_name] = value

        return parameters, errors

    def _get_parameter(self, param, request):
        name = param["name"]
        deprecated = param.getkey("deprecated", False)
        if deprecated:
            warnings.warn(
                f"{name} parameter is deprecated",
                DeprecationWarning,
            )

        param_location = param["in"]
        location = request.parameters[param_location]
        try:
            return self._get_param_or_header_value(param, location)
        except KeyError:
            required = param.getkey("required", False)
            if required:
                raise MissingRequiredParameter(name)
            raise MissingParameter(name)

    def _get_security(self, request, operation):
        security = None
        if "security" in self.spec:
            security = self.spec / "security"
        if "security" in operation:
            security = operation / "security"

        if not security:
            return {}

        for security_requirement in security:
            try:
                return {
                    scheme_name: self._get_security_value(scheme_name, request)
                    for scheme_name in list(security_requirement.keys())
                }
            except SecurityError:
                continue

        raise InvalidSecurity()

    def _get_security_value(self, scheme_name, request):
        security_schemes = self.spec / "components#securitySchemes"
        if scheme_name not in security_schemes:
            return
        scheme = security_schemes[scheme_name]
        security_provider = self.security_provider_factory.create(scheme)
        return security_provider(request)

    def _get_body(self, request, operation):
        if "requestBody" not in operation:
            return None, []

        request_body = operation / "requestBody"

        try:
            raw_body = self._get_body_value(request_body, request)
        except MissingRequiredRequestBody as exc:
            return None, [exc]
        except MissingRequestBody:
            return None, []

        try:
            media_type, mimetype = self._get_media_type(
                request_body / "content", request.mimetype
            )
        except MediaTypeFinderError as exc:
            return None, [exc]

        try:
            deserialised = self._deserialise_data(mimetype, raw_body)
        except DeserializeError as exc:
            return None, [exc]

        try:
            casted = self._cast(media_type, deserialised)
        except CastError as exc:
            return None, [exc]

        if "schema" not in media_type:
            return casted, []

        schema = media_type / "schema"
        try:
            body = self._unmarshal(schema, casted)
        except (ValidateError, UnmarshalError) as exc:
            return None, [exc]

        return body, []

    def _get_body_value(self, request_body, request):
        if not request.body:
            if request_body.getkey("required", False):
                raise MissingRequiredRequestBody(request)
            raise MissingRequestBody(request)
        return request.body


class RequestParametersValidator(BaseRequestValidator):
    def validate(self, request):
        try:
            path, operation, _, path_result, _ = self._find_path(
                request.method, request.full_url_pattern
            )
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        params, params_errors = self._get_parameters(request, path, operation)

        return RequestValidationResult(
            errors=params_errors,
            parameters=params,
        )


class RequestBodyValidator(BaseRequestValidator):
    def validate(self, request):
        try:
            _, operation, _, _, _ = self._find_path(
                request.method, request.full_url_pattern
            )
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        body, body_errors = self._get_body(request, operation)

        return RequestValidationResult(
            errors=body_errors,
            body=body,
        )


class RequestSecurityValidator(BaseRequestValidator):
    def validate(self, request):
        try:
            _, operation, _, _, _ = self._find_path(
                request.method, request.full_url_pattern
            )
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        try:
            security = self._get_security(request, operation)
        except InvalidSecurity as exc:
            return RequestValidationResult(errors=[exc])

        return RequestValidationResult(
            errors=[],
            security=security,
        )


class RequestValidator(BaseRequestValidator):
    def validate(self, request):
        try:
            path, operation, _, path_result, _ = self._find_path(
                request.method, request.full_url_pattern
            )
        # don't process if operation errors
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        try:
            security = self._get_security(request, operation)
        except InvalidSecurity as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        params, params_errors = self._get_parameters(request, path, operation)

        body, body_errors = self._get_body(request, operation)

        errors = params_errors + body_errors
        return RequestValidationResult(
            errors=errors,
            body=body,
            parameters=params,
            security=security,
        )
