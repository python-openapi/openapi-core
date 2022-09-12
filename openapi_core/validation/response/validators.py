"""OpenAPI core validation response validators module"""
import warnings
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from openapi_core.casting.schemas.exceptions import CastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.exceptions import OpenAPIError
from openapi_core.spec import Spec
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.templating.responses.exceptions import ResponseFinderError
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.exceptions import UnmarshalError
from openapi_core.unmarshalling.schemas.exceptions import ValidateError
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory,
)
from openapi_core.util import chainiters
from openapi_core.validation.exceptions import MissingHeader
from openapi_core.validation.exceptions import MissingRequiredHeader
from openapi_core.validation.request.protocols import Request
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.exceptions import HeadersError
from openapi_core.validation.response.exceptions import MissingResponseContent
from openapi_core.validation.response.protocols import Response
from openapi_core.validation.validators import BaseValidator


class BaseResponseValidator(BaseValidator):
    def iter_errors(
        self,
        spec: Spec,
        request: Request,
        response: Response,
        base_url: Optional[str] = None,
    ) -> Iterator[Exception]:
        result = self.validate(spec, request, response, base_url=base_url)
        yield from result.errors

    def validate(
        self,
        spec: Spec,
        request: Request,
        response: Response,
        base_url: Optional[str] = None,
    ) -> ResponseValidationResult:
        raise NotImplementedError

    def _find_operation_response(
        self,
        spec: Spec,
        request: Request,
        response: Response,
        base_url: Optional[str] = None,
    ) -> Spec:
        _, operation, _, _, _ = self._find_path(
            spec, request, base_url=base_url
        )
        return self._get_operation_response(operation, response)

    def _get_operation_response(
        self, operation: Spec, response: Response
    ) -> Spec:
        from openapi_core.templating.responses.finders import ResponseFinder

        finder = ResponseFinder(operation / "responses")
        return finder.find(str(response.status_code))

    def _get_data(self, response: Response, operation_response: Spec) -> Any:
        if "content" not in operation_response:
            return None

        media_type, mimetype = self._get_media_type(
            operation_response / "content", response.mimetype
        )
        raw_data = self._get_data_value(response)
        deserialised = self._deserialise_data(mimetype, raw_data)
        casted = self._cast(media_type, deserialised)

        if "schema" not in media_type:
            return casted

        schema = media_type / "schema"
        data = self._unmarshal(schema, casted)

        return data

    def _get_data_value(self, response: Response) -> Any:
        if not response.data:
            raise MissingResponseContent(response)

        return response.data

    def _get_headers(
        self, response: Response, operation_response: Spec
    ) -> Dict[str, Any]:
        if "headers" not in operation_response:
            return {}

        headers = operation_response / "headers"

        errors: List[OpenAPIError] = []
        validated: Dict[str, Any] = {}
        for name, header in list(headers.items()):
            # ignore Content-Type header
            if name.lower() == "content-type":
                continue
            try:
                value = self._get_header(name, header, response)
            except MissingHeader:
                continue
            except (
                MissingRequiredHeader,
                DeserializeError,
                CastError,
                ValidateError,
                UnmarshalError,
            ) as exc:
                errors.append(exc)
                continue
            else:
                validated[name] = value

        if errors:
            raise HeadersError(context=iter(errors), headers=validated)

        return validated

    def _get_header(self, name: str, header: Spec, response: Response) -> Any:
        deprecated = header.getkey("deprecated", False)
        if deprecated:
            warnings.warn(
                f"{name} header is deprecated",
                DeprecationWarning,
            )

        try:
            return self._get_param_or_header_value(
                header, response.headers, name=name
            )
        except KeyError:
            required = header.getkey("required", False)
            if required:
                raise MissingRequiredHeader(name)
            raise MissingHeader(name)


class ResponseDataValidator(BaseResponseValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        response: Response,
        base_url: Optional[str] = None,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._find_operation_response(
                spec,
                request,
                response,
                base_url=base_url,
            )
        # don't process if operation errors
        except (PathError, ResponseFinderError) as exc:
            return ResponseValidationResult(errors=[exc])

        try:
            data = self._get_data(response, operation_response)
        except (
            MediaTypeFinderError,
            MissingResponseContent,
            DeserializeError,
            CastError,
            ValidateError,
            UnmarshalError,
        ) as exc:
            data = None
            data_errors = [exc]
        else:
            data_errors = []

        return ResponseValidationResult(
            errors=data_errors,
            data=data,
        )


class ResponseHeadersValidator(BaseResponseValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        response: Response,
        base_url: Optional[str] = None,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._find_operation_response(
                spec,
                request,
                response,
                base_url=base_url,
            )
        # don't process if operation errors
        except (PathError, ResponseFinderError) as exc:
            return ResponseValidationResult(errors=[exc])

        try:
            headers = self._get_headers(response, operation_response)
        except HeadersError as exc:
            headers = exc.headers
            headers_errors = exc.context
        else:
            headers_errors = []

        return ResponseValidationResult(
            errors=headers_errors,
            headers=headers,
        )


class ResponseValidator(BaseResponseValidator):
    def validate(
        self,
        spec: Spec,
        request: Request,
        response: Response,
        base_url: Optional[str] = None,
    ) -> ResponseValidationResult:
        try:
            operation_response = self._find_operation_response(
                spec,
                request,
                response,
                base_url=base_url,
            )
        # don't process if operation errors
        except (PathError, ResponseFinderError) as exc:
            return ResponseValidationResult(errors=[exc])

        try:
            data = self._get_data(response, operation_response)
        except (
            MediaTypeFinderError,
            MissingResponseContent,
            DeserializeError,
            CastError,
            ValidateError,
            UnmarshalError,
        ) as exc:
            data = None
            data_errors = [exc]
        else:
            data_errors = []

        try:
            headers = self._get_headers(response, operation_response)
        except HeadersError as exc:
            headers = exc.headers
            headers_errors = exc.context
        else:
            headers_errors = []

        errors = list(chainiters(data_errors, headers_errors))
        return ResponseValidationResult(
            errors=errors,
            data=data,
            headers=headers,
        )
