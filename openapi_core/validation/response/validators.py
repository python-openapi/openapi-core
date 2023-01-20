"""OpenAPI core validation response validators module"""
import warnings
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional
from urllib.parse import urljoin

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.exceptions import OpenAPIError
from openapi_core.spec import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.templating.paths.datatypes import PathOperationServer
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.paths.finders import APICallPathFinder
from openapi_core.templating.paths.finders import WebhookPathFinder
from openapi_core.templating.responses.exceptions import ResponseFinderError
from openapi_core.unmarshalling.schemas import (
    oas30_response_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.util import chainiters
from openapi_core.validation.decorators import ValidationErrorWrapper
from openapi_core.validation.exceptions import ValidationError
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.request.protocols import WebhookRequest
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.exceptions import DataError
from openapi_core.validation.response.exceptions import HeaderError
from openapi_core.validation.response.exceptions import HeadersError
from openapi_core.validation.response.exceptions import InvalidData
from openapi_core.validation.response.exceptions import InvalidHeader
from openapi_core.validation.response.exceptions import MissingData
from openapi_core.validation.response.exceptions import MissingHeader
from openapi_core.validation.response.exceptions import MissingRequiredHeader
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.validators import BaseAPICallValidator
from openapi_core.validation.validators import BaseValidator
from openapi_core.validation.validators import BaseWebhookValidator


class BaseResponseValidator(BaseValidator):
    def _validate(
        self,
        status_code: int,
        data: str,
        headers: Mapping[str, Any],
        mimetype: str,
        operation: Spec,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._get_operation_response(
                status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            return ResponseValidationResult(errors=[exc])

        try:
            validated_data = self._get_data(data, mimetype, operation_response)
        except DataError as exc:
            validated_data = None
            data_errors = [exc]
        else:
            data_errors = []

        try:
            validated_headers = self._get_headers(headers, operation_response)
        except HeadersError as exc:
            validated_headers = exc.headers
            headers_errors = exc.context
        else:
            headers_errors = []

        errors = list(chainiters(data_errors, headers_errors))
        return ResponseValidationResult(
            errors=errors,
            data=validated_data,
            headers=validated_headers,
        )

    def _validate_data(
        self, status_code: int, data: str, mimetype: str, operation: Spec
    ) -> ResponseValidationResult:
        try:
            operation_response = self._get_operation_response(
                status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            return ResponseValidationResult(errors=[exc])

        try:
            validated = self._get_data(data, mimetype, operation_response)
        except DataError as exc:
            validated = None
            data_errors = [exc]
        else:
            data_errors = []

        return ResponseValidationResult(
            errors=data_errors,
            data=validated,
        )

    def _validate_headers(
        self, status_code: int, headers: Mapping[str, Any], operation: Spec
    ) -> ResponseValidationResult:
        try:
            operation_response = self._get_operation_response(
                status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            return ResponseValidationResult(errors=[exc])

        try:
            validated = self._get_headers(headers, operation_response)
        except HeadersError as exc:
            validated = exc.headers
            headers_errors = exc.context
        else:
            headers_errors = []

        return ResponseValidationResult(
            errors=headers_errors,
            headers=validated,
        )

    def _get_operation_response(
        self,
        status_code: int,
        operation: Spec,
    ) -> Spec:
        from openapi_core.templating.responses.finders import ResponseFinder

        finder = ResponseFinder(operation / "responses")
        return finder.find(str(status_code))

    @ValidationErrorWrapper(DataError, InvalidData)
    def _get_data(
        self, data: str, mimetype: str, operation_response: Spec
    ) -> Any:
        if "content" not in operation_response:
            return None

        media_type, mimetype = self._get_media_type(
            operation_response / "content", mimetype
        )
        raw_data = self._get_data_value(data)
        deserialised = self._deserialise_data(mimetype, raw_data)
        casted = self._cast(media_type, deserialised)

        if "schema" not in media_type:
            return casted

        schema = media_type / "schema"
        data = self._unmarshal(schema, casted)

        return data

    def _get_data_value(self, data: str) -> Any:
        if not data:
            raise MissingData

        return data

    def _get_headers(
        self, headers: Mapping[str, Any], operation_response: Spec
    ) -> Dict[str, Any]:
        if "headers" not in operation_response:
            return {}

        response_headers = operation_response / "headers"

        errors: List[OpenAPIError] = []
        validated: Dict[str, Any] = {}
        for name, header in list(response_headers.items()):
            # ignore Content-Type header
            if name.lower() == "content-type":
                continue
            try:
                value = self._get_header(headers, name, header)
            except MissingHeader:
                continue
            except ValidationError as exc:
                errors.append(exc)
                continue
            else:
                validated[name] = value

        if errors:
            raise HeadersError(context=iter(errors), headers=validated)

        return validated

    @ValidationErrorWrapper(HeaderError, InvalidHeader, name="name")
    def _get_header(
        self, headers: Mapping[str, Any], name: str, header: Spec
    ) -> Any:
        deprecated = header.getkey("deprecated", False)
        if deprecated:
            warnings.warn(
                f"{name} header is deprecated",
                DeprecationWarning,
            )

        try:
            return self._get_param_or_header_value(header, headers, name=name)
        except KeyError:
            required = header.getkey("required", False)
            if required:
                raise MissingRequiredHeader(name)
            raise MissingHeader(name)


class BaseAPICallResponseValidator(
    BaseResponseValidator, BaseAPICallValidator
):
    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        result = self.validate(request, response)
        yield from result.errors

    def validate(
        self,
        request: Request,
        response: Response,
    ) -> ResponseValidationResult:
        raise NotImplementedError


class BaseWebhookResponseValidator(
    BaseResponseValidator, BaseWebhookValidator
):
    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        result = self.validate(request, response)
        yield from result.errors

    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseValidationResult:
        raise NotImplementedError


class ResponseDataValidator(BaseAPICallResponseValidator):
    def validate(
        self,
        request: Request,
        response: Response,
    ) -> ResponseValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseValidationResult(errors=[exc])

        return self._validate_data(
            response.status_code, response.data, response.mimetype, operation
        )


class ResponseHeadersValidator(BaseAPICallResponseValidator):
    def validate(
        self,
        request: Request,
        response: Response,
    ) -> ResponseValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseValidationResult(errors=[exc])

        return self._validate_headers(
            response.status_code, response.headers, operation
        )


class ResponseValidator(BaseAPICallResponseValidator):
    def validate(
        self,
        request: Request,
        response: Response,
    ) -> ResponseValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseValidationResult(errors=[exc])

        return self._validate(
            response.status_code,
            response.data,
            response.headers,
            response.mimetype,
            operation,
        )


class WebhookResponseDataValidator(BaseWebhookResponseValidator):
    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseValidationResult(errors=[exc])

        return self._validate_data(
            response.status_code, response.data, response.mimetype, operation
        )


class WebhookResponseHeadersValidator(BaseWebhookResponseValidator):
    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseValidationResult(errors=[exc])

        return self._validate_headers(
            response.status_code, response.headers, operation
        )


class WebhookResponseValidator(BaseWebhookResponseValidator):
    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseValidationResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseValidationResult(errors=[exc])

        return self._validate(
            response.status_code,
            response.data,
            response.headers,
            response.mimetype,
            operation,
        )


class V30ResponseDataValidator(ResponseDataValidator):
    schema_unmarshallers_factory = oas30_response_schema_unmarshallers_factory


class V30ResponseHeadersValidator(ResponseHeadersValidator):
    schema_unmarshallers_factory = oas30_response_schema_unmarshallers_factory


class V30ResponseValidator(ResponseValidator):
    schema_unmarshallers_factory = oas30_response_schema_unmarshallers_factory


class V31ResponseDataValidator(ResponseDataValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31ResponseHeadersValidator(ResponseHeadersValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31ResponseValidator(ResponseValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookResponseDataValidator(WebhookResponseDataValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookResponseHeadersValidator(WebhookResponseHeadersValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookResponseValidator(WebhookResponseValidator):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
