"""OpenAPI core validation response validators module"""

import warnings
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional

from jsonschema_path import SchemaPath
from openapi_spec_validator import OpenAPIV30SpecValidator
from openapi_spec_validator import OpenAPIV31SpecValidator

from openapi_core.casting.schemas import oas30_read_schema_casters_factory
from openapi_core.casting.schemas import oas31_schema_casters_factory
from openapi_core.exceptions import OpenAPIError
from openapi_core.protocols import HeadersType
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.responses.exceptions import ResponseFinderError
from openapi_core.validation.decorators import ValidationErrorWrapper
from openapi_core.validation.exceptions import ValidationError
from openapi_core.validation.response.exceptions import DataValidationError
from openapi_core.validation.response.exceptions import HeadersError
from openapi_core.validation.response.exceptions import HeaderValidationError
from openapi_core.validation.response.exceptions import InvalidData
from openapi_core.validation.response.exceptions import InvalidHeader
from openapi_core.validation.response.exceptions import MissingData
from openapi_core.validation.response.exceptions import MissingHeader
from openapi_core.validation.response.exceptions import MissingRequiredHeader
from openapi_core.validation.schemas import (
    oas30_read_schema_validators_factory,
)
from openapi_core.validation.schemas import oas31_schema_validators_factory
from openapi_core.validation.validators import BaseAPICallValidator
from openapi_core.validation.validators import BaseValidator
from openapi_core.validation.validators import BaseWebhookValidator


class BaseResponseValidator(BaseValidator):
    def _iter_errors(
        self,
        status_code: int,
        data: Optional[bytes],
        headers: HeadersType,
        mimetype: str,
        operation: SchemaPath,
    ) -> Iterator[Exception]:
        try:
            operation_response = self._find_operation_response(
                status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            yield exc
            return

        try:
            self._get_data(data, mimetype, operation_response)
        except DataValidationError as exc:
            yield exc

        try:
            self._get_headers(headers, operation_response)
        except HeadersError as exc:
            yield from exc.context

    def _iter_data_errors(
        self,
        status_code: int,
        data: Optional[bytes],
        mimetype: str,
        operation: SchemaPath,
    ) -> Iterator[Exception]:
        try:
            operation_response = self._find_operation_response(
                status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            yield exc
            return

        try:
            self._get_data(data, mimetype, operation_response)
        except DataValidationError as exc:
            yield exc

    def _iter_headers_errors(
        self,
        status_code: int,
        headers: HeadersType,
        operation: SchemaPath,
    ) -> Iterator[Exception]:
        try:
            operation_response = self._find_operation_response(
                status_code, operation
            )
        # don't process if operation errors
        except ResponseFinderError as exc:
            yield exc
            return

        try:
            self._get_headers(headers, operation_response)
        except HeadersError as exc:
            yield from exc.context

    def _find_operation_response(
        self,
        status_code: int,
        operation: SchemaPath,
    ) -> SchemaPath:
        from openapi_core.templating.responses.finders import ResponseFinder

        finder = ResponseFinder(operation / "responses")
        return finder.find(str(status_code))

    @ValidationErrorWrapper(DataValidationError, InvalidData)
    def _get_data(
        self,
        data: Optional[bytes],
        mimetype: str,
        operation_response: SchemaPath,
    ) -> Any:
        if "content" not in operation_response:
            return None

        content = operation_response / "content"

        raw_data = self._get_data_value(data)
        value, _ = self._get_content_and_schema(raw_data, content, mimetype)
        return value

    def _get_data_value(self, data: Optional[bytes]) -> bytes:
        if not data:
            raise MissingData

        return data

    def _get_headers(
        self, headers: HeadersType, operation_response: SchemaPath
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

    @ValidationErrorWrapper(HeaderValidationError, InvalidHeader, name="name")
    def _get_header(
        self, headers: Mapping[str, Any], name: str, header: SchemaPath
    ) -> Any:
        deprecated = header.getkey("deprecated", False)
        if deprecated:
            warnings.warn(
                f"{name} header is deprecated",
                DeprecationWarning,
            )

        try:
            value, _ = self._get_param_or_header_and_schema(
                header, headers, name=name
            )
        except KeyError:
            required = header.getkey("required", False)
            if required:
                raise MissingRequiredHeader(name)
            raise MissingHeader(name)
        else:
            return value


class BaseAPICallResponseValidator(
    BaseResponseValidator, BaseAPICallValidator
):
    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        raise NotImplementedError

    def validate(
        self,
        request: Request,
        response: Response,
    ) -> None:
        for err in self.iter_errors(request, response):
            raise err


class BaseWebhookResponseValidator(
    BaseResponseValidator, BaseWebhookValidator
):
    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        raise NotImplementedError

    def validate(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> None:
        for err in self.iter_errors(request, response):
            raise err


class APICallResponseDataValidator(BaseAPICallResponseValidator):
    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        yield from self._iter_data_errors(
            response.status_code,
            response.data,
            response.content_type,
            operation,
        )


class APICallResponseHeadersValidator(BaseAPICallResponseValidator):
    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        yield from self._iter_headers_errors(
            response.status_code, response.headers, operation
        )


class APICallResponseValidator(BaseAPICallResponseValidator):
    def iter_errors(
        self,
        request: Request,
        response: Response,
    ) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        yield from self._iter_errors(
            response.status_code,
            response.data,
            response.headers,
            response.content_type,
            operation,
        )


class WebhookResponseDataValidator(BaseWebhookResponseValidator):
    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        yield from self._iter_data_errors(
            response.status_code,
            response.data,
            response.content_type,
            operation,
        )


class WebhookResponseHeadersValidator(BaseWebhookResponseValidator):
    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        yield from self._iter_headers_errors(
            response.status_code, response.headers, operation
        )


class WebhookResponseValidator(BaseWebhookResponseValidator):
    def iter_errors(
        self,
        request: WebhookRequest,
        response: Response,
    ) -> Iterator[Exception]:
        try:
            _, operation, _, _, _ = self._find_path(request)
        # don't process if operation errors
        except PathError as exc:
            yield exc
            return

        yield from self._iter_errors(
            response.status_code,
            response.data,
            response.headers,
            response.content_type,
            operation,
        )


class V30ResponseDataValidator(APICallResponseDataValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_read_schema_casters_factory
    schema_validators_factory = oas30_read_schema_validators_factory


class V30ResponseHeadersValidator(APICallResponseHeadersValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_read_schema_casters_factory
    schema_validators_factory = oas30_read_schema_validators_factory


class V30ResponseValidator(APICallResponseValidator):
    spec_validator_cls = OpenAPIV30SpecValidator
    schema_casters_factory = oas30_read_schema_casters_factory
    schema_validators_factory = oas30_read_schema_validators_factory


class V31ResponseDataValidator(APICallResponseDataValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31ResponseHeadersValidator(APICallResponseHeadersValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31ResponseValidator(APICallResponseValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookResponseDataValidator(WebhookResponseDataValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookResponseHeadersValidator(WebhookResponseHeadersValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory


class V31WebhookResponseValidator(WebhookResponseValidator):
    spec_validator_cls = OpenAPIV31SpecValidator
    schema_casters_factory = oas31_schema_casters_factory
    schema_validators_factory = oas31_schema_validators_factory
