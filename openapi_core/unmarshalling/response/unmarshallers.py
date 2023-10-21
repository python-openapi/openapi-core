from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.responses.exceptions import ResponseFinderError
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.schemas import (
    oas30_read_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.schemas import (
    oas31_schema_unmarshallers_factory,
)
from openapi_core.unmarshalling.unmarshallers import BaseUnmarshaller
from openapi_core.util import chainiters
from openapi_core.validation.response.exceptions import DataValidationError
from openapi_core.validation.response.exceptions import HeadersError
from openapi_core.validation.response.validators import (
    APICallResponseValidator,
)
from openapi_core.validation.response.validators import BaseResponseValidator
from openapi_core.validation.response.validators import (
    V30ResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    V30ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import V30ResponseValidator
from openapi_core.validation.response.validators import (
    V31ResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    V31ResponseHeadersValidator,
)
from openapi_core.validation.response.validators import V31ResponseValidator
from openapi_core.validation.response.validators import (
    V31WebhookResponseDataValidator,
)
from openapi_core.validation.response.validators import (
    V31WebhookResponseHeadersValidator,
)
from openapi_core.validation.response.validators import (
    V31WebhookResponseValidator,
)
from openapi_core.validation.response.validators import (
    WebhookResponseValidator,
)


class BaseResponseUnmarshaller(BaseResponseValidator, BaseUnmarshaller):
    def _unmarshal(
        self,
        response: Response,
        operation: SchemaPath,
    ) -> ResponseUnmarshalResult:
        try:
            operation_response = self._find_operation_response(
                response.status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        try:
            validated_data = self._get_data(
                response.data, response.content_type, operation_response
            )
        except DataValidationError as exc:
            validated_data = None
            data_errors = [exc]
        else:
            data_errors = []

        try:
            validated_headers = self._get_headers(
                response.headers, operation_response
            )
        except HeadersError as exc:
            validated_headers = exc.headers
            headers_errors = exc.context
        else:
            headers_errors = []

        errors = list(chainiters(data_errors, headers_errors))
        return ResponseUnmarshalResult(
            errors=errors,
            data=validated_data,
            headers=validated_headers,
        )

    def _unmarshal_data(
        self,
        response: Response,
        operation: SchemaPath,
    ) -> ResponseUnmarshalResult:
        try:
            operation_response = self._find_operation_response(
                response.status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        try:
            validated = self._get_data(
                response.data, response.content_type, operation_response
            )
        except DataValidationError as exc:
            validated = None
            data_errors = [exc]
        else:
            data_errors = []

        return ResponseUnmarshalResult(
            errors=data_errors,
            data=validated,
        )

    def _unmarshal_headers(
        self,
        response: Response,
        operation: SchemaPath,
    ) -> ResponseUnmarshalResult:
        try:
            operation_response = self._find_operation_response(
                response.status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        try:
            validated = self._get_headers(response.headers, operation_response)
        except HeadersError as exc:
            validated = exc.headers
            headers_errors = exc.context
        else:
            headers_errors = []

        return ResponseUnmarshalResult(
            errors=headers_errors,
            headers=validated,
        )


class APICallResponseUnmarshaller(
    APICallResponseValidator, BaseResponseUnmarshaller
):
    def unmarshal(
        self,
        request: Request,
        response: Response,
    ) -> ResponseUnmarshalResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        return self._unmarshal(response, operation)


class APICallResponseDataUnmarshaller(
    APICallResponseValidator, BaseResponseUnmarshaller
):
    def unmarshal(
        self,
        request: Request,
        response: Response,
    ) -> ResponseUnmarshalResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        return self._unmarshal_data(response, operation)


class APICallResponseHeadersUnmarshaller(
    APICallResponseValidator, BaseResponseUnmarshaller
):
    def unmarshal(
        self,
        request: Request,
        response: Response,
    ) -> ResponseUnmarshalResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        return self._unmarshal_headers(response, operation)


class WebhookResponseUnmarshaller(
    WebhookResponseValidator, BaseResponseUnmarshaller
):
    def unmarshal(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseUnmarshalResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        return self._unmarshal(response, operation)


class WebhookResponseDataUnmarshaller(
    WebhookResponseValidator, BaseResponseUnmarshaller
):
    def unmarshal(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseUnmarshalResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        return self._unmarshal_data(response, operation)


class WebhookResponseHeadersUnmarshaller(
    WebhookResponseValidator, BaseResponseUnmarshaller
):
    def unmarshal(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> ResponseUnmarshalResult:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            return ResponseUnmarshalResult(errors=[exc])

        return self._unmarshal_headers(response, operation)


class V30ResponseDataUnmarshaller(
    V30ResponseDataValidator, APICallResponseDataUnmarshaller
):
    schema_unmarshallers_factory = oas30_read_schema_unmarshallers_factory


class V30ResponseHeadersUnmarshaller(
    V30ResponseHeadersValidator, APICallResponseHeadersUnmarshaller
):
    schema_unmarshallers_factory = oas30_read_schema_unmarshallers_factory


class V30ResponseUnmarshaller(
    V30ResponseValidator, APICallResponseUnmarshaller
):
    schema_unmarshallers_factory = oas30_read_schema_unmarshallers_factory


class V31ResponseDataUnmarshaller(
    V31ResponseDataValidator, APICallResponseDataUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31ResponseHeadersUnmarshaller(
    V31ResponseHeadersValidator, APICallResponseHeadersUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31ResponseUnmarshaller(
    V31ResponseValidator, APICallResponseUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookResponseDataUnmarshaller(
    V31WebhookResponseDataValidator, WebhookResponseDataUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookResponseHeadersUnmarshaller(
    V31WebhookResponseHeadersValidator, WebhookResponseHeadersUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory


class V31WebhookResponseUnmarshaller(
    V31WebhookResponseValidator, WebhookResponseUnmarshaller
):
    schema_unmarshallers_factory = oas31_schema_unmarshallers_factory
