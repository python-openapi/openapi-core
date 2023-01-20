"""OpenAPI core validation request validators module"""
import warnings
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Optional
from urllib.parse import urljoin

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
from openapi_core.security.exceptions import SecurityProviderError
from openapi_core.security.factories import SecurityProviderFactory
from openapi_core.spec.paths import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.paths.finders import APICallPathFinder
from openapi_core.templating.paths.finders import WebhookPathFinder
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.unmarshalling.schemas import (
    oas30_request_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.util import chainiters
from openapi_core.validation.decorators import ValidationErrorWrapper
from openapi_core.validation.request.datatypes import Parameters
from openapi_core.validation.request.datatypes import RequestParameters
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.exceptions import InvalidParameter
from openapi_core.validation.request.exceptions import InvalidRequestBody
from openapi_core.validation.request.exceptions import InvalidSecurity
from openapi_core.validation.request.exceptions import MissingParameter
from openapi_core.validation.request.exceptions import MissingRequestBody
from openapi_core.validation.request.exceptions import MissingRequiredParameter
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
)
from openapi_core.validation.request.exceptions import ParameterError
from openapi_core.validation.request.exceptions import ParametersError
from openapi_core.validation.request.exceptions import RequestBodyError
from openapi_core.validation.request.exceptions import SecurityError
from openapi_core.validation.request.protocols import BaseRequest
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import WebhookRequest
from openapi_core.validation.validators import BaseAPICallValidator
from openapi_core.validation.validators import BaseValidator
from openapi_core.validation.validators import BaseWebhookValidator


class BaseRequestValidator(BaseValidator):
    def __init__(
        self,
        spec: Spec,
        base_url: Optional[str] = None,
        schema_unmarshallers_factory: Optional[
            SchemaUnmarshallersFactory
        ] = None,
        schema_casters_factory: SchemaCastersFactory = schema_casters_factory,
        parameter_deserializers_factory: ParameterDeserializersFactory = parameter_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
        security_provider_factory: SecurityProviderFactory = security_provider_factory,
    ):
        super().__init__(
            spec,
            base_url=base_url,
            schema_unmarshallers_factory=schema_unmarshallers_factory,
            schema_casters_factory=schema_casters_factory,
            parameter_deserializers_factory=parameter_deserializers_factory,
            media_type_deserializers_factory=media_type_deserializers_factory,
        )
        self.security_provider_factory = security_provider_factory

    def _validate(
        self, request: BaseRequest, operation: Spec, path: Spec
    ) -> RequestValidationResult:
        try:
            security = self._get_security(request.parameters, operation)
        except SecurityError as exc:
            return RequestValidationResult(errors=[exc])

        try:
            params = self._get_parameters(request.parameters, operation, path)
        except ParametersError as exc:
            params = exc.parameters
            params_errors = exc.context
        else:
            params_errors = []

        try:
            body = self._get_body(request.body, request.mimetype, operation)
        except MissingRequestBody:
            body = None
            body_errors = []
        except RequestBodyError as exc:
            body = None
            body_errors = [exc]
        else:
            body_errors = []

        errors = list(chainiters(params_errors, body_errors))
        return RequestValidationResult(
            errors=errors,
            body=body,
            parameters=params,
            security=security,
        )

    def _validate_body(
        self, request: BaseRequest, operation: Spec
    ) -> RequestValidationResult:
        try:
            body = self._get_body(request.body, request.mimetype, operation)
        except MissingRequestBody:
            body = None
            errors = []
        except RequestBodyError as exc:
            body = None
            errors = [exc]
        else:
            errors = []

        return RequestValidationResult(
            errors=errors,
            body=body,
        )

    def _validate_parameters(
        self, request: BaseRequest, operation: Spec, path: Spec
    ) -> RequestValidationResult:
        try:
            params = self._get_parameters(request.parameters, path, operation)
        except ParametersError as exc:
            params = exc.parameters
            params_errors = exc.context
        else:
            params_errors = []

        return RequestValidationResult(
            errors=params_errors,
            parameters=params,
        )

    def _validate_security(
        self, request: BaseRequest, operation: Spec
    ) -> RequestValidationResult:
        try:
            security = self._get_security(request.parameters, operation)
        except SecurityError as exc:
            return RequestValidationResult(errors=[exc])

        return RequestValidationResult(
            errors=[],
            security=security,
        )

    def _get_parameters(
        self,
        parameters: RequestParameters,
        operation: Spec,
        path: Spec,
    ) -> Parameters:
        operation_params = operation.get("parameters", [])
        path_params = path.get("parameters", [])

        errors = []
        seen = set()
        validated = Parameters()
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
                value = self._get_parameter(parameters, param)
            except MissingParameter:
                continue
            except ParameterError as exc:
                errors.append(exc)
                continue
            else:
                location = getattr(validated, param_location)
                location[param_name] = value

        if errors:
            raise ParametersError(errors=errors, parameters=validated)

        return validated

    @ValidationErrorWrapper(
        ParameterError,
        InvalidParameter,
        "from_spec",
        spec="param",
    )
    def _get_parameter(
        self, parameters: RequestParameters, param: Spec
    ) -> Any:
        name = param["name"]
        deprecated = param.getkey("deprecated", False)
        if deprecated:
            warnings.warn(
                f"{name} parameter is deprecated",
                DeprecationWarning,
            )

        param_location = param["in"]
        location = parameters[param_location]
        try:
            return self._get_param_or_header_value(param, location)
        except KeyError:
            required = param.getkey("required", False)
            if required:
                raise MissingRequiredParameter(name, param_location)
            raise MissingParameter(name, param_location)

    @ValidationErrorWrapper(SecurityError, InvalidSecurity)
    def _get_security(
        self, parameters: RequestParameters, operation: Spec
    ) -> Optional[Dict[str, str]]:
        security = None
        if "security" in self.spec:
            security = self.spec / "security"
        if "security" in operation:
            security = operation / "security"

        if not security:
            return {}

        schemes = []
        for security_requirement in security:
            try:
                scheme_names = list(security_requirement.keys())
                schemes.append(scheme_names)
                return {
                    scheme_name: self._get_security_value(
                        parameters, scheme_name
                    )
                    for scheme_name in scheme_names
                }
            except SecurityProviderError:
                continue

        raise SecurityNotFound(schemes)

    def _get_security_value(
        self, parameters: RequestParameters, scheme_name: str
    ) -> Any:
        security_schemes = self.spec / "components#securitySchemes"
        if scheme_name not in security_schemes:
            return
        scheme = security_schemes[scheme_name]
        security_provider = self.security_provider_factory.create(scheme)
        return security_provider(parameters)

    @ValidationErrorWrapper(RequestBodyError, InvalidRequestBody)
    def _get_body(
        self, body: Optional[str], mimetype: str, operation: Spec
    ) -> Any:
        if "requestBody" not in operation:
            return None

        request_body = operation / "requestBody"

        raw_body = self._get_body_value(body, request_body)
        media_type, mimetype = self._get_media_type(
            request_body / "content", mimetype
        )
        deserialised = self._deserialise_data(mimetype, raw_body)
        casted = self._cast(media_type, deserialised)

        if "schema" not in media_type:
            return casted

        schema = media_type / "schema"
        unmarshalled = self._unmarshal(schema, casted)
        return unmarshalled

    def _get_body_value(self, body: Optional[str], request_body: Spec) -> Any:
        if not body:
            if request_body.getkey("required", False):
                raise MissingRequiredRequestBody
            raise MissingRequestBody
        return body


class BaseAPICallRequestValidator(BaseRequestValidator, BaseAPICallValidator):
    def iter_errors(self, request: Request) -> Iterator[Exception]:
        result = self.validate(request)
        yield from result.errors

    def validate(self, request: Request) -> RequestValidationResult:
        raise NotImplementedError


class BaseWebhookRequestValidator(BaseRequestValidator, BaseWebhookValidator):
    def iter_errors(self, request: WebhookRequest) -> Iterator[Exception]:
        result = self.validate(request)
        yield from result.errors

    def validate(self, request: WebhookRequest) -> RequestValidationResult:
        raise NotImplementedError


class RequestBodyValidator(BaseAPICallRequestValidator):
    def validate(self, request: Request) -> RequestValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        return self._validate_body(request, operation)


class RequestParametersValidator(BaseAPICallRequestValidator):
    def validate(self, request: Request) -> RequestValidationResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._validate_parameters(request, operation, path)


class RequestSecurityValidator(BaseAPICallRequestValidator):
    def validate(self, request: Request) -> RequestValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        return self._validate_security(request, operation)


class RequestValidator(BaseAPICallRequestValidator):
    def validate(self, request: Request) -> RequestValidationResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._validate(request, operation, path)


class WebhookRequestValidator(BaseWebhookRequestValidator):
    def validate(self, request: WebhookRequest) -> RequestValidationResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._validate(request, operation, path)


class WebhookRequestBodyValidator(BaseWebhookRequestValidator):
    def validate(self, request: WebhookRequest) -> RequestValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        return self._validate_body(request, operation)


class WebhookRequestParametersValidator(BaseWebhookRequestValidator):
    def validate(self, request: WebhookRequest) -> RequestValidationResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._validate_parameters(request, operation, path)


class WebhookRequestSecurityValidator(BaseWebhookRequestValidator):
    def validate(self, request: WebhookRequest) -> RequestValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc])

        return self._validate_security(request, operation)


class V30RequestBodyValidator(RequestBodyValidator):
    schema_unmarshallers_factory = oas30_request_schema_unmarshallers_factory


class V30RequestParametersValidator(RequestParametersValidator):
    schema_unmarshallers_factory = oas30_request_schema_unmarshallers_factory


class V30RequestSecurityValidator(RequestSecurityValidator):
    schema_unmarshallers_factory = oas30_request_schema_unmarshallers_factory


class V30RequestValidator(RequestValidator):
    schema_unmarshallers_factory = oas30_request_schema_unmarshallers_factory


class V31RequestBodyValidator(RequestBodyValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31RequestParametersValidator(RequestParametersValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31RequestSecurityValidator(RequestSecurityValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31RequestValidator(RequestValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
    path_finder_cls = WebhookPathFinder


class V31WebhookRequestBodyValidator(WebhookRequestBodyValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
    path_finder_cls = WebhookPathFinder


class V31WebhookRequestParametersValidator(WebhookRequestParametersValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
    path_finder_cls = WebhookPathFinder


class V31WebhookRequestSecurityValidator(WebhookRequestSecurityValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
    path_finder_cls = WebhookPathFinder


class V31WebhookRequestValidator(WebhookRequestValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
    path_finder_cls = WebhookPathFinder
