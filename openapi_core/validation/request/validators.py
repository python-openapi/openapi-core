"""OpenAPI core validation request validators module"""
import warnings
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Optional

from openapi_core.casting.schemas import schema_casters_factory
from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.media_types import (
    media_type_deserializers_factory,
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
from openapi_core.exceptions import OpenAPIError
from openapi_core.security import security_provider_factory
from openapi_core.security.exceptions import SecurityError
from openapi_core.security.factories import SecurityProviderFactory
from openapi_core.spec.paths import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.util import chainiters
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.exceptions import MissingParameter
from openapi_core.validation.exceptions import MissingRequiredParameter
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.exceptions import MissingRequestBody
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
)
from openapi_core.validation.request.exceptions import ParametersError
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.validators import BaseValidator


class BaseRequestValidator(BaseValidator):
    def __init__(
        self,
        schema_unmarshallers_factory: SchemaUnmarshallersFactory,
        schema_casters_factory: SchemaCastersFactory = schema_casters_factory,
        parameter_deserializers_factory: ParameterDeserializersFactory = parameter_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
        security_provider_factory: SecurityProviderFactory = security_provider_factory,
    ):
        super().__init__(
            schema_unmarshallers_factory,
            schema_casters_factory=schema_casters_factory,
            parameter_deserializers_factory=parameter_deserializers_factory,
            media_type_deserializers_factory=media_type_deserializers_factory,
        )
        self.security_provider_factory = security_provider_factory

    def iter_errors(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> Iterator[Exception]:
        result = self.validate(spec, request, base_url=base_url)
        yield from result.errors

    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        raise NotImplementedError

    def _get_parameters(
        self, request: Request, path: Spec, operation: Spec
    ) -> Parameters:
        operation_params = operation.get("parameters", [])
        path_params = path.get("parameters", [])

        errors = []
        seen = set()
        parameters = Parameters()
        params_iter = chainiters(operation_params, path_params)
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

        if errors:
            raise ParametersError(context=errors, parameters=parameters)

        return parameters

    def _get_parameter(self, param: Spec, request: Request) -> Any:
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

    def _get_security(
        self, spec: Spec, request: Request, operation: Spec
    ) -> Optional[Dict[str, str]]:
        security = None
        if "security" in spec:
            security = spec / "security"
        if "security" in operation:
            security = operation / "security"

        if not security:
            return {}

        for security_requirement in security:
            try:
                return {
                    scheme_name: self._get_security_value(
                        spec, scheme_name, request
                    )
                    for scheme_name in list(security_requirement.keys())
                }
            except SecurityError:
                continue

        raise InvalidSecurity

    def _get_security_value(
        self, spec: Spec, scheme_name: str, request: Request
    ) -> Any:
        security_schemes = spec / "components#securitySchemes"
        if scheme_name not in security_schemes:
            return
        scheme = security_schemes[scheme_name]
        security_provider = self.security_provider_factory.create(scheme)
        return security_provider(request)

    def _get_body(self, request: Request, operation: Spec) -> Any:
        if "requestBody" not in operation:
            return None

        request_body = operation / "requestBody"

        raw_body = self._get_body_value(request_body, request)
        media_type, mimetype = self._get_media_type(
            request_body / "content", request.mimetype
        )
        deserialised = self._deserialise_data(mimetype, raw_body)
        casted = self._cast(media_type, deserialised)

        if "schema" not in media_type:
            return casted

        schema = media_type / "schema"
        body = self._unmarshal(schema, casted)

        return body

    def _get_body_value(self, request_body: Spec, request: Request) -> Any:
        if not request.body:
            if request_body.getkey("required", False):
                raise MissingRequiredRequestBody(request)
            raise MissingRequestBody(request)
        return request.body


class RequestParametersValidator(BaseRequestValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        try:
            path, operation, _, path_result, _ = self._find_path(
                spec, request, base_url=base_url
            )
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        try:
            params = self._get_parameters(request, path, operation)
        except ParametersError as exc:
            params = exc.parameters
            params_errors = exc.context
        else:
            params_errors = []

        return RequestValidationResult(
            errors=params_errors,
            parameters=params,
        )


class RequestBodyValidator(BaseRequestValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(
                spec, request, base_url=base_url
            )
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        try:
            body = self._get_body(request, operation)
        except (
            MissingRequiredRequestBody,
            MediaTypeFinderError,
            DeserializeError,
            CastError,
            ValidateError,
            UnmarshalError,
        ) as exc:
            body = None
            errors = [exc]
        except MissingRequestBody:
            body = None
            errors = []
        else:
            errors = []

        return RequestValidationResult(
            errors=errors,
            body=body,
        )


class RequestSecurityValidator(BaseRequestValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(
                spec, request, base_url=base_url
            )
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        try:
            security = self._get_security(spec, request, operation)
        except InvalidSecurity as exc:
            return RequestValidationResult(errors=[exc])

        return RequestValidationResult(
            errors=[],
            security=security,
        )


class RequestValidator(BaseRequestValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        base_url: Optional[str] = None,
    ) -> RequestValidationResult:
        try:
            path, operation, _, path_result, _ = self._find_path(
                spec, request, base_url=base_url
            )
        # don't process if operation errors
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        try:
            security = self._get_security(spec, request, operation)
        except InvalidSecurity as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        try:
            params = self._get_parameters(request, path, operation)
        except ParametersError as exc:
            params = exc.parameters
            params_errors = exc.context
        else:
            params_errors = []

        try:
            body = self._get_body(request, operation)
        except (
            MissingRequiredRequestBody,
            MediaTypeFinderError,
            DeserializeError,
            CastError,
            ValidateError,
            UnmarshalError,
        ) as exc:
            body = None
            body_errors = [exc]
        except MissingRequestBody:
            body = None
            body_errors = []
        else:
            body_errors = []

        errors = list(chainiters(params_errors, body_errors))
        return RequestValidationResult(
            errors=errors,
            body=body,
            parameters=params,
            security=security,
        )
