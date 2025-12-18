"""OpenAPI core validation request validators module"""

import warnings
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Optional

from jsonschema_path import SchemaPath
from openapi_spec_validator import OpenAPIV30SpecValidator
from openapi_spec_validator import OpenAPIV31SpecValidator
from openapi_spec_validator.validation.types import SpecValidatorType

from openapi_core.casting.schemas import oas30_write_schema_casters_factory
from openapi_core.casting.schemas import oas31_schema_casters_factory
from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.datatypes import Parameters
from openapi_core.datatypes import RequestParameters
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.protocols import BaseRequest
from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest
from openapi_core.security import security_provider_factory
from openapi_core.security.exceptions import SecurityProviderError
from openapi_core.security.factories import SecurityProviderFactory
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.paths.types import PathFinderType
from openapi_core.templating.security.exceptions import SecurityNotFound
from openapi_core.util import chainiters
from openapi_core.validation.decorators import ValidationErrorWrapper
from openapi_core.validation.request.exceptions import InvalidParameter
from openapi_core.validation.request.exceptions import InvalidRequestBody
from openapi_core.validation.request.exceptions import InvalidSecurity
from openapi_core.validation.request.exceptions import MissingParameter
from openapi_core.validation.request.exceptions import MissingRequestBody
from openapi_core.validation.request.exceptions import MissingRequiredParameter
from openapi_core.validation.request.exceptions import (
    MissingRequiredRequestBody,
)
from openapi_core.validation.request.exceptions import ParametersError
from openapi_core.validation.request.exceptions import ParameterValidationError
from openapi_core.validation.request.exceptions import (
    RequestBodyValidationError,
)
from openapi_core.validation.request.exceptions import SecurityValidationError
from openapi_core.validation.schemas import (
    oas30_write_schema_validators_factory,
)
from openapi_core.validation.schemas import oas31_schema_validators_factory
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory
from openapi_core.validation.validators import BaseAPICallValidator
from openapi_core.validation.validators import BaseValidator
from openapi_core.validation.validators import BaseWebhookValidator


class BaseRequestValidator(BaseValidator):
    def __init__(
        self,
        spec: SchemaPath,
        base_url: Optional[str] = None,
        style_deserializers_factory: Optional[
            StyleDeserializersFactory
        ] = None,
        media_type_deserializers_factory: Optional[
            MediaTypeDeserializersFactory
        ] = None,
        schema_casters_factory: Optional[SchemaCastersFactory] = None,
        schema_validators_factory: Optional[SchemaValidatorsFactory] = None,
        path_finder_cls: Optional[PathFinderType] = None,
        spec_validator_cls: Optional[SpecValidatorType] = None,
        format_validators: Optional[FormatValidatorsDict] = None,
        extra_format_validators: Optional[FormatValidatorsDict] = None,
        extra_media_type_deserializers: Optional[
            MediaTypeDeserializersDict
        ] = None,
        security_provider_factory: SecurityProviderFactory = security_provider_factory,
    ):

        BaseValidator.__init__(
            self,
            spec,
            base_url=base_url,
            style_deserializers_factory=style_deserializers_factory,
            media_type_deserializers_factory=media_type_deserializers_factory,
            schema_casters_factory=schema_casters_factory,
            schema_validators_factory=schema_validators_factory,
            path_finder_cls=path_finder_cls,
            spec_validator_cls=spec_validator_cls,
            format_validators=format_validators,
            extra_format_validators=extra_format_validators,
            extra_media_type_deserializers=extra_media_type_deserializers,
        )
        self.security_provider_factory = security_provider_factory

    def _iter_errors(
        self, request: BaseRequest, operation: SchemaPath, path: SchemaPath
    ) -> Iterator[Exception]:
        try:
            self._get_security(request.parameters, operation)
        # don't process if security errors
        except SecurityValidationError as exc:
            yield exc
            return

        try:
            self._get_parameters(request.parameters, operation, path)
        except ParametersError as exc:
            yield from exc.errors

        try:
            self._get_body(request.body, request.content_type, operation)
        except MissingRequestBody:
            pass
        except RequestBodyValidationError as exc:
            yield exc

    def _iter_body_errors(
        self, request: BaseRequest, operation: SchemaPath
    ) -> Iterator[Exception]:
        try:
            self._get_body(request.body, request.content_type, operation)
        except RequestBodyValidationError as exc:
            yield exc

    def _iter_parameters_errors(
        self, request: BaseRequest, operation: SchemaPath, path: SchemaPath
    ) -> Iterator[Exception]:
        try:
            self._get_parameters(request.parameters, path, operation)
        except ParametersError as exc:
            yield from exc.errors

    def _iter_security_errors(
        self, request: BaseRequest, operation: SchemaPath
    ) -> Iterator[Exception]:
        try:
            self._get_security(request.parameters, operation)
        except SecurityValidationError as exc:
            yield exc

    def _get_parameters(
        self,
        parameters: RequestParameters,
        operation: SchemaPath,
        path: SchemaPath,
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
            except ParameterValidationError as exc:
                errors.append(exc)
                continue
            else:
                location = getattr(validated, param_location)
                location[param_name] = value

        if errors:
            raise ParametersError(errors=errors, parameters=validated)

        return validated

    @ValidationErrorWrapper(
        ParameterValidationError,
        InvalidParameter,
        "from_spec",
        spec="param",
    )
    def _get_parameter(
        self, parameters: RequestParameters, param: SchemaPath
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
            value, _ = self._get_param_or_header_and_schema(param, location)
        except KeyError:
            required = param.getkey("required", False)
            if required:
                raise MissingRequiredParameter(name, param_location)
            raise MissingParameter(name, param_location)
        else:
            return value

    @ValidationErrorWrapper(SecurityValidationError, InvalidSecurity)
    def _get_security(
        self, parameters: RequestParameters, operation: SchemaPath
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

    @ValidationErrorWrapper(RequestBodyValidationError, InvalidRequestBody)
    def _get_body(
        self, body: Optional[bytes], mimetype: str, operation: SchemaPath
    ) -> Any:
        if "requestBody" not in operation:
            return None

        # TODO: implement required flag checking
        request_body = operation / "requestBody"
        content = request_body / "content"

        raw_body = self._get_body_value(body, request_body)
        value, _ = self._get_content_and_schema(raw_body, content, mimetype)
        return value

    def _get_body_value(
        self, body: Optional[bytes], request_body: SchemaPath
    ) -> bytes:
        if not body:
            if request_body.getkey("required", False):
                raise MissingRequiredRequestBody
            raise MissingRequestBody
        return body


class BaseAPICallRequestValidator(BaseRequestValidator, BaseAPICallValidator):
    def iter_errors(self, request: Request) -> Iterator[Exception]:
        raise NotImplementedError

    def validate(self, request: Request) -> None:
        for err in self.iter_errors(request):
            raise err


class BaseWebhookRequestValidator(BaseRequestValidator, BaseWebhookValidator):
    def iter_errors(self, request: WebhookRequest) -> Iterator[Exception]:
        raise NotImplementedError

    def validate(self, request: WebhookRequest) -> None:
        for err in self.iter_errors(request):
            raise err


class APICallRequestBodyValidator(BaseAPICallRequestValidator):
    def iter_errors(self, request: Request) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            yield exc
            return

        yield from self._iter_body_errors(request, operation)


class APICallRequestParametersValidator(BaseAPICallRequestValidator):
    def iter_errors(self, request: Request) -> Iterator[Exception]:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        except PathError as exc:
            yield exc
            return

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        yield from self._iter_parameters_errors(request, operation, path)


class APICallRequestSecurityValidator(BaseAPICallRequestValidator):
    def iter_errors(self, request: Request) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            yield exc
            return

        yield from self._iter_security_errors(request, operation)


class APICallRequestValidator(BaseAPICallRequestValidator):
    def iter_errors(self, request: Request) -> Iterator[Exception]:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        yield from self._iter_errors(request, operation, path)


class WebhookRequestValidator(BaseWebhookRequestValidator):
    def iter_errors(self, request: WebhookRequest) -> Iterator[Exception]:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        yield from self._iter_errors(request, operation, path)


class WebhookRequestBodyValidator(BaseWebhookRequestValidator):
    def iter_errors(self, request: WebhookRequest) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            yield exc
            return

        yield from self._iter_body_errors(request, operation)


class WebhookRequestParametersValidator(BaseWebhookRequestValidator):
    def iter_errors(self, request: WebhookRequest) -> Iterator[Exception]:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        except PathError as exc:
            yield exc
            return

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        yield from self._iter_parameters_errors(request, operation, path)


class WebhookRequestSecurityValidator(BaseWebhookRequestValidator):
    def iter_errors(self, request: WebhookRequest) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        except PathError as exc:
            yield exc
            return

        yield from self._iter_security_errors(request, operation)


class V30RequestBodyValidator(APICallRequestBodyValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_write_schema_casters_factory
    schema_validators_factory = oas30_write_schema_validators_factory


class V30RequestParametersValidator(APICallRequestParametersValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_write_schema_casters_factory
    schema_validators_factory = oas30_write_schema_validators_factory


class V30RequestSecurityValidator(APICallRequestSecurityValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_write_schema_casters_factory
    schema_validators_factory = oas30_write_schema_validators_factory


class V30RequestValidator(APICallRequestValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_write_schema_casters_factory
    schema_validators_factory = oas30_write_schema_validators_factory


class V31RequestBodyValidator(APICallRequestBodyValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31RequestParametersValidator(APICallRequestParametersValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31RequestSecurityValidator(APICallRequestSecurityValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31RequestValidator(APICallRequestValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookRequestBodyValidator(WebhookRequestBodyValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookRequestParametersValidator(WebhookRequestParametersValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookRequestSecurityValidator(WebhookRequestSecurityValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookRequestValidator(WebhookRequestValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory
