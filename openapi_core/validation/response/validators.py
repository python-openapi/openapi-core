"""OpenAPI core validation response validators module"""
from typing import Any, Dict, Sequence, Tuple
import warnings

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.exceptions import (
    MissingHeader, MissingRequiredHeader,
)
from openapi_core.spec.paths import SpecPath
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.responses.exceptions import ResponseFinderError
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalError, ValidateError,
)
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.response.datatypes import (
    OpenAPIResponse, ResponseValidationResult,
)
from openapi_core.validation.response.exceptions import MissingResponseContent
from openapi_core.validation.response.types import DataErrors, HeadersErrors
from openapi_core.validation.validators import BaseValidator


class BaseResponseValidator(BaseValidator):

    @property
    def schema_unmarshallers_factory(self) -> SchemaUnmarshallersFactory:
        spec_resolver = self.spec.accessor.dereferencer.resolver_manager.\
            resolver
        return SchemaUnmarshallersFactory(
            spec_resolver, self.format_checker,
            self.custom_formatters, context=UnmarshalContext.RESPONSE,
        )

    def _find_operation_response(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> SpecPath:
        _, operation, _, _, _ = self._find_path(request)
        return self._get_operation_response(
                operation, response)

    def _get_operation_response(
        self,
        operation: SpecPath,
        response: OpenAPIResponse,
    ) -> SpecPath:
        from openapi_core.templating.responses.finders import ResponseFinder
        finder = ResponseFinder(operation / 'responses')
        return finder.find(str(response.status_code))

    def _get_data(
        self,
        response: OpenAPIResponse,
        operation_response: SpecPath,
    ) -> Tuple[Any, Sequence[DataErrors]]:
        if 'content' not in operation_response:
            return None, []

        try:
            media_type, mimetype = self._get_media_type(
                operation_response / 'content', response)
        except MediaTypeFinderError as exc:
            return None, [exc, ]

        try:
            raw_data = self._get_data_value(response)
        except MissingResponseContent as exc:
            return None, [exc, ]

        try:
            deserialised = self._deserialise_data(mimetype, raw_data)
        except DeserializeError as exc:
            return None, [exc, ]

        try:
            casted = self._cast(media_type, deserialised)
        except CastError as exc:
            return None, [exc, ]

        if 'schema' not in media_type:
            return casted, []

        schema = media_type / 'schema'
        try:
            data = self._unmarshal(schema, casted)
        except (ValidateError, UnmarshalError) as exc:
            return None, [exc, ]

        return data, []

    def _get_data_value(self, response: OpenAPIResponse) -> str:
        if not response.data:
            raise MissingResponseContent(response)

        return response.data

    def _get_headers(
        self,
        response: OpenAPIResponse,
        operation_response: SpecPath,
    ) -> Tuple[Dict, Sequence[HeadersErrors]]:
        if 'headers' not in operation_response:
            return {}, []

        headers = operation_response / 'headers'

        errors = []
        validated = {}
        for name, header in list(headers.items()):
            # ignore Content-Type header
            if name.lower() == "content-type":
                continue
            try:
                value = self._get_header(name, header, response)
            except MissingHeader:
                continue
            except (
                MissingRequiredHeader, DeserializeError,
                CastError, ValidateError, UnmarshalError,
            ) as exc:
                errors.append(exc)
                continue
            else:
                validated[name] = value

        return validated, errors

    def _get_header(
        self,
        name: str,
        header: SpecPath,
        response: OpenAPIResponse,
    ) -> Any:
        deprecated = header.getkey('deprecated', False)
        if deprecated:
            warnings.warn(
                f"{name} header is deprecated",
                DeprecationWarning,
            )

        try:
            return self._get_param_or_header_value(
                header, response.headers, name=name)
        except KeyError:
            required = header.getkey('required', False)
            if required:
                raise MissingRequiredHeader(name)
            raise MissingHeader(name)


class ResponseDataValidator(BaseResponseValidator):

    def validate(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._find_operation_response(
                request, response)
        # don't process if operation errors
        except (PathError, ResponseFinderError) as exc:
            return ResponseValidationResult(errors=[exc, ])

        data, data_errors = self._get_data(response, operation_response)

        return ResponseValidationResult(
            errors=data_errors,
            data=data,
        )


class ResponseHeadersValidator(BaseResponseValidator):

    def validate(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._find_operation_response(
                request, response)
        # don't process if operation errors
        except (PathError, ResponseFinderError) as exc:
            return ResponseValidationResult(errors=[exc, ])

        headers, headers_errors = self._get_headers(
            response, operation_response)

        return ResponseValidationResult(
            errors=headers_errors,
            headers=headers,
        )


class ResponseValidator(BaseResponseValidator):

    def validate(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._find_operation_response(
                request, response)
        # don't process if operation errors
        except (PathError, ResponseFinderError) as exc:
            return ResponseValidationResult(errors=[exc, ])

        data, data_errors = self._get_data(response, operation_response)

        headers, headers_errors = self._get_headers(
            response, operation_response)

        errors = data_errors + headers_errors
        return ResponseValidationResult(
            errors=errors,
            data=data,
            headers=headers,
        )
