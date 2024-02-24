from typing import Optional

from jsonschema_path import SchemaPath
from openapi_spec_validator.validation.types import SpecValidatorType

from openapi_core.casting.schemas.factories import SchemaCastersFactory
from openapi_core.deserializing.media_types import (
    media_type_deserializers_factory,
)
from openapi_core.deserializing.media_types.datatypes import (
    MediaTypeDeserializersDict,
)
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.deserializing.styles import style_deserializers_factory
from openapi_core.deserializing.styles.factories import (
    StyleDeserializersFactory,
)
from openapi_core.protocols import BaseRequest
from openapi_core.protocols import Request
from openapi_core.protocols import WebhookRequest
from openapi_core.security import security_provider_factory
from openapi_core.security.factories import SecurityProviderFactory
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.paths.types import PathFinderType
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.schemas import (
    oas30_write_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas.datatypes import (
    FormatUnmarshallersDict,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.unmarshalling.unmarshallers import BaseUnmarshaller
from openapi_core.util import chainiters
from openapi_core.validation.request.exceptions import MissingRequestBody
from openapi_core.validation.request.exceptions import ParametersError
from openapi_core.validation.request.exceptions import (
    RequestBodyValidationError,
)
from openapi_core.validation.request.exceptions import SecurityValidationError
from openapi_core.validation.request.validators import APICallRequestValidator
from openapi_core.validation.request.validators import BaseRequestValidator
from openapi_core.validation.request.validators import V30RequestBodyValidator
from openapi_core.validation.request.validators import (
    V30RequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V30RequestSecurityValidator,
)
from openapi_core.validation.request.validators import V30RequestValidator
from openapi_core.validation.request.validators import V31RequestBodyValidator
from openapi_core.validation.request.validators import (
    V31RequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V31RequestSecurityValidator,
)
from openapi_core.validation.request.validators import V31RequestValidator
from openapi_core.validation.request.validators import (
    V31WebhookRequestBodyValidator,
)
from openapi_core.validation.request.validators import (
    V31WebhookRequestParametersValidator,
)
from openapi_core.validation.request.validators import (
    V31WebhookRequestSecurityValidator,
)
from openapi_core.validation.request.validators import (
    V31WebhookRequestValidator,
)
from openapi_core.validation.request.validators import WebhookRequestValidator
from openapi_core.validation.schemas.datatypes import FormatValidatorsDict
from openapi_core.validation.schemas.factories import SchemaValidatorsFactory


class BaseRequestUnmarshaller(BaseRequestValidator, BaseUnmarshaller):
    def __init__(
        self,
        spec: SchemaPath,
        base_url: Optional[str] = None,
        style_deserializers_factory: StyleDeserializersFactory = style_deserializers_factory,
        media_type_deserializers_factory: MediaTypeDeserializersFactory = media_type_deserializers_factory,
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
        schema_unmarshallers_factory: Optional[
            SchemaUnmarshallersFactory
        ] = None,
        format_unmarshallers: Optional[FormatUnmarshallersDict] = None,
        extra_format_unmarshallers: Optional[FormatUnmarshallersDict] = None,
    ):
        BaseUnmarshaller.__init__(
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
            schema_unmarshallers_factory=schema_unmarshallers_factory,
            format_unmarshallers=format_unmarshallers,
            extra_format_unmarshallers=extra_format_unmarshallers,
        )
        BaseRequestValidator.__init__(
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
            security_provider_factory=security_provider_factory,
        )

    def _unmarshal(
        self, request: BaseRequest, operation: SchemaPath, path: SchemaPath
    ) -> RequestUnmarshalResult:
        try:
            security = self._get_security(request.parameters, operation)
        except SecurityValidationError as exc:
            return RequestUnmarshalResult(errors=[exc])

        try:
            params = self._get_parameters(request.parameters, operation, path)
        except ParametersError as exc:
            params = exc.parameters
            params_errors = exc.errors
        else:
            params_errors = []

        try:
            body = self._get_body(
                request.body, request.content_type, operation
            )
        except MissingRequestBody:
            body = None
            body_errors = []
        except RequestBodyValidationError as exc:
            body = None
            body_errors = [exc]
        else:
            body_errors = []

        errors = list(chainiters(params_errors, body_errors))
        return RequestUnmarshalResult(
            errors=errors,
            body=body,
            parameters=params,
            security=security,
        )

    def _unmarshal_body(
        self, request: BaseRequest, operation: SchemaPath, path: SchemaPath
    ) -> RequestUnmarshalResult:
        try:
            body = self._get_body(
                request.body, request.content_type, operation
            )
        except MissingRequestBody:
            body = None
            errors = []
        except RequestBodyValidationError as exc:
            body = None
            errors = [exc]
        else:
            errors = []

        return RequestUnmarshalResult(
            errors=errors,
            body=body,
        )

    def _unmarshal_parameters(
        self, request: BaseRequest, operation: SchemaPath, path: SchemaPath
    ) -> RequestUnmarshalResult:
        try:
            params = self._get_parameters(request.parameters, path, operation)
        except ParametersError as exc:
            params = exc.parameters
            params_errors = exc.errors
        else:
            params_errors = []

        return RequestUnmarshalResult(
            errors=params_errors,
            parameters=params,
        )

    def _unmarshal_security(
        self, request: BaseRequest, operation: SchemaPath, path: SchemaPath
    ) -> RequestUnmarshalResult:
        try:
            security = self._get_security(request.parameters, operation)
        except SecurityValidationError as exc:
            return RequestUnmarshalResult(errors=[exc])

        return RequestUnmarshalResult(
            errors=[],
            security=security,
        )


class BaseAPICallRequestUnmarshaller(BaseRequestUnmarshaller):
    pass


class BaseWebhookRequestUnmarshaller(BaseRequestUnmarshaller):
    pass


class APICallRequestUnmarshaller(
    APICallRequestValidator, BaseAPICallRequestUnmarshaller
):
    def unmarshal(self, request: Request) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal(request, operation, path)


class APICallRequestBodyUnmarshaller(
    APICallRequestValidator, BaseAPICallRequestUnmarshaller
):
    def unmarshal(self, request: Request) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal_body(request, operation, path)


class APICallRequestParametersUnmarshaller(
    APICallRequestValidator, BaseAPICallRequestUnmarshaller
):
    def unmarshal(self, request: Request) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal_parameters(request, operation, path)


class APICallRequestSecurityUnmarshaller(
    APICallRequestValidator, BaseAPICallRequestUnmarshaller
):
    def unmarshal(self, request: Request) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal_security(request, operation, path)


class WebhookRequestUnmarshaller(
    WebhookRequestValidator, BaseWebhookRequestUnmarshaller
):
    def unmarshal(self, request: WebhookRequest) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal(request, operation, path)


class WebhookRequestBodyUnmarshaller(
    WebhookRequestValidator, BaseWebhookRequestUnmarshaller
):
    def unmarshal(self, request: WebhookRequest) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal_body(request, operation, path)


class WebhookRequestParametersUnmarshaller(
    WebhookRequestValidator, BaseWebhookRequestUnmarshaller
):
    def unmarshal(self, request: WebhookRequest) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal_parameters(request, operation, path)


class WebhookRequestSecuritysUnmarshaller(
    WebhookRequestValidator, BaseWebhookRequestUnmarshaller
):
    def unmarshal(self, request: WebhookRequest) -> RequestUnmarshalResult:
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return RequestUnmarshalResult(errors=[exc])

        request.parameters.path = (
            request.parameters.path or path_result.variables
        )

        return self._unmarshal_security(request, operation, path)


class V30RequestBodyUnmarshaller(
    V30RequestBodyValidator, APICallRequestBodyUnmarshaller
):
    schema_unmarshallers_factory = oas30_write_schema_unmarshallers_factory


class V30RequestParametersUnmarshaller(
    V30RequestParametersValidator, APICallRequestParametersUnmarshaller
):
    schema_unmarshallers_factory = oas30_write_schema_unmarshallers_factory


class V30RequestSecurityUnmarshaller(
    V30RequestSecurityValidator, APICallRequestSecurityUnmarshaller
):
    schema_unmarshallers_factory = oas30_write_schema_unmarshallers_factory


class V30RequestUnmarshaller(V30RequestValidator, APICallRequestUnmarshaller):
    schema_unmarshallers_factory = oas30_write_schema_unmarshallers_factory


class V31RequestBodyUnmarshaller(
    V31RequestBodyValidator, APICallRequestBodyUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31RequestParametersUnmarshaller(
    V31RequestParametersValidator, APICallRequestParametersUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31RequestSecurityUnmarshaller(
    V31RequestSecurityValidator, APICallRequestSecurityUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31RequestUnmarshaller(V31RequestValidator, APICallRequestUnmarshaller):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookRequestBodyUnmarshaller(
    V31WebhookRequestBodyValidator, WebhookRequestBodyUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookRequestParametersUnmarshaller(
    V31WebhookRequestParametersValidator, WebhookRequestParametersUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookRequestSecurityUnmarshaller(
    V31WebhookRequestSecurityValidator, WebhookRequestSecuritysUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookRequestUnmarshaller(
    V31WebhookRequestValidator, WebhookRequestUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
