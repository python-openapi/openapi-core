"""OpenAPI core app module"""

from functools import cached_property
from pathlib import Path
from typing import Optional

from jsonschema._utils import Unset
from jsonschema.validators import _UNSET
from jsonschema_path import SchemaPath
from jsonschema_path.handlers.protocols import SupportsRead
from jsonschema_path.typing import Schema
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import ValidatorDetectError
from openapi_spec_validator.versions.datatypes import SpecVersion
from openapi_spec_validator.versions.exceptions import OpenAPIVersionNotFound
from openapi_spec_validator.versions.shortcuts import get_spec_version
from typing_extensions import Annotated
from typing_extensions import Doc

from openapi_core.configurations import Config
from openapi_core.exceptions import SpecError
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.protocols import WebhookRequest
from openapi_core.types import AnyRequest
from openapi_core.unmarshalling.request import (
    UNMARSHALLERS as REQUEST_UNMARSHALLERS,
)
from openapi_core.unmarshalling.request import (
    WEBHOOK_UNMARSHALLERS as WEBHOOK_REQUEST_UNMARSHALLERS,
)
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.protocols import RequestUnmarshaller
from openapi_core.unmarshalling.request.protocols import (
    WebhookRequestUnmarshaller,
)
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType
from openapi_core.unmarshalling.request.types import (
    WebhookRequestUnmarshallerType,
)
from openapi_core.unmarshalling.response import (
    UNMARSHALLERS as RESPONSE_UNMARSHALLERS,
)
from openapi_core.unmarshalling.response import (
    WEBHOOK_UNMARSHALLERS as WEBHOOK_RESPONSE_UNMARSHALLERS,
)
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.protocols import ResponseUnmarshaller
from openapi_core.unmarshalling.response.protocols import (
    WebhookResponseUnmarshaller,
)
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType
from openapi_core.unmarshalling.response.types import (
    WebhookResponseUnmarshallerType,
)
from openapi_core.validation.request import VALIDATORS as REQUEST_VALIDATORS
from openapi_core.validation.request import (
    WEBHOOK_VALIDATORS as WEBHOOK_REQUEST_VALIDATORS,
)
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.request.protocols import WebhookRequestValidator
from openapi_core.validation.request.types import RequestValidatorType
from openapi_core.validation.request.types import WebhookRequestValidatorType
from openapi_core.validation.response import VALIDATORS as RESPONSE_VALIDATORS
from openapi_core.validation.response import (
    WEBHOOK_VALIDATORS as WEBHOOK_RESPONSE_VALIDATORS,
)
from openapi_core.validation.response.protocols import ResponseValidator
from openapi_core.validation.response.protocols import WebhookResponseValidator
from openapi_core.validation.response.types import ResponseValidatorType
from openapi_core.validation.response.types import WebhookResponseValidatorType


class OpenAPI:
    """`OpenAPI` application class, the main entrypoint class for OpenAPI-core.

    OpenAPI can be created in multiple ways: from existing memory data or from storage such as local disk via ``from_*()`` APIs

    Read more information, in the
    [OpenAPI-core docs for First Steps](https://openapi-core.readthedocs.io/#first-steps).

    Examples:
        You can import the OpenAPI class directly from openapi_core:

        Create an OpenAPI from a dictionary:

        ```python
        from openapi_core import OpenAPI

        app = OpenAPI.from_dict(spec)
        ```

        Create an OpenAPI from a path object:

        ```python
        from openapi_core import OpenAPI

        app = OpenAPI.from_path(path)
        ```

        Create an OpenAPI from a file path:

        ```python
        from openapi_core import OpenAPI

        app = OpenAPI.from_file_path('spec.yaml')
        ```

        Create an OpenAPI from a file object:

        ```python
        from openapi_core import OpenAPI

        with open('spec.yaml') as f:
            app = OpenAPI.from_file(f)
        ```

    """

    def __init__(
        self,
        spec: Annotated[
            SchemaPath,
            Doc(
                """
                OpenAPI specification schema path object.
                """
            ),
        ],
        config: Annotated[
            Optional[Config],
            Doc(
                """
                Configuration object for the OpenAPI application.
                """
            ),
        ] = None,
    ):
        if not isinstance(spec, SchemaPath):
            raise TypeError("'spec' argument is not type of SchemaPath")

        self.spec = spec
        self.config = config or Config()

        self.check_spec()

    @classmethod
    def from_dict(
        cls,
        data: Annotated[
            Schema,
            Doc(
                """
                Dictionary representing the OpenAPI specification.
                """
            ),
        ],
        config: Annotated[
            Optional[Config],
            Doc(
                """
                Configuration object for the OpenAPI application.
                """
            ),
        ] = None,
        base_uri: Annotated[
            str,
            Doc(
                """
                Base URI for the OpenAPI specification.
                """
            ),
        ] = "",
    ) -> "OpenAPI":
        """Creates an `OpenAPI` from a dictionary.

        Example:
        ```python
        from openapi_core import OpenAPI

        app = OpenAPI.from_dict(spec)
        ```

        Returns:
            OpenAPI: An instance of the OpenAPI class.
        """
        sp = SchemaPath.from_dict(data, base_uri=base_uri)
        return cls(sp, config=config)

    @classmethod
    def from_path(
        cls,
        path: Annotated[
            Path,
            Doc(
                """
                Path object representing the OpenAPI specification file.
                """
            ),
        ],
        config: Annotated[
            Optional[Config],
            Doc(
                """
                Configuration object for the OpenAPI application.
                """
            ),
        ] = None,
    ) -> "OpenAPI":
        """Creates an `OpenAPI` from a [Path object](https://docs.python.org/3/library/pathlib.html#pathlib.Path).

        Example:
        ```python
        from openapi_core import OpenAPI

        app = OpenAPI.from_path(path)
        ```

        Returns:
            OpenAPI: An instance of the OpenAPI class.
        """
        sp = SchemaPath.from_path(path)
        return cls(sp, config=config)

    @classmethod
    def from_file_path(
        cls,
        file_path: Annotated[
            str,
            Doc(
                """
                File path string representing the OpenAPI specification file.
                """
            ),
        ],
        config: Annotated[
            Optional[Config],
            Doc(
                """
                Configuration object for the OpenAPI application.
                """
            ),
        ] = None,
    ) -> "OpenAPI":
        """Creates an `OpenAPI` from a file path string.

        Example:
        ```python
        from openapi_core import OpenAPI

        app = OpenAPI.from_file_path('spec.yaml')
        ```

        Returns:
            OpenAPI: An instance of the OpenAPI class.
        """
        sp = SchemaPath.from_file_path(file_path)
        return cls(sp, config=config)

    @classmethod
    def from_file(
        cls,
        fileobj: Annotated[
            SupportsRead,
            Doc(
                """
                File object representing the OpenAPI specification file.
                """
            ),
        ],
        config: Annotated[
            Optional[Config],
            Doc(
                """
                Configuration object for the OpenAPI application.
                """
            ),
        ] = None,
        base_uri: Annotated[
            str,
            Doc(
                """
                Base URI for the OpenAPI specification.
                """
            ),
        ] = "",
    ) -> "OpenAPI":
        """Creates an `OpenAPI` from a [file object](https://docs.python.org/3/glossary.html#term-file-object).

        Example:
        ```python
        from openapi_core import OpenAPI

        with open('spec.yaml') as f:
            app = OpenAPI.from_file(f)
        ```

        Returns:
            OpenAPI: An instance of the OpenAPI class.
        """
        sp = SchemaPath.from_file(fileobj, base_uri=base_uri)
        return cls(sp, config=config)

    def _get_version(self) -> SpecVersion:
        try:
            return get_spec_version(self.spec.contents())
        # backward compatibility
        except OpenAPIVersionNotFound:
            raise SpecError("Spec schema version not detected")

    def check_spec(self) -> None:
        if self.config.spec_validator_cls is None:
            return

        cls = None
        if self.config.spec_validator_cls is not _UNSET:
            cls = self.config.spec_validator_cls

        try:
            validate(
                self.spec.contents(),
                base_uri=self.config.spec_base_uri
                or self.spec.accessor.resolver._base_uri,  # type: ignore[attr-defined]
                cls=cls,
            )
        except ValidatorDetectError:
            raise SpecError("spec not detected")

    @property
    def version(self) -> SpecVersion:
        return self._get_version()

    @cached_property
    def request_validator_cls(self) -> Optional[RequestValidatorType]:
        if not isinstance(self.config.request_validator_cls, Unset):
            return self.config.request_validator_cls
        return REQUEST_VALIDATORS.get(self.version)

    @cached_property
    def response_validator_cls(self) -> Optional[ResponseValidatorType]:
        if not isinstance(self.config.response_validator_cls, Unset):
            return self.config.response_validator_cls
        return RESPONSE_VALIDATORS.get(self.version)

    @cached_property
    def webhook_request_validator_cls(
        self,
    ) -> Optional[WebhookRequestValidatorType]:
        if not isinstance(self.config.webhook_request_validator_cls, Unset):
            return self.config.webhook_request_validator_cls
        return WEBHOOK_REQUEST_VALIDATORS.get(self.version)

    @cached_property
    def webhook_response_validator_cls(
        self,
    ) -> Optional[WebhookResponseValidatorType]:
        if not isinstance(self.config.webhook_response_validator_cls, Unset):
            return self.config.webhook_response_validator_cls
        return WEBHOOK_RESPONSE_VALIDATORS.get(self.version)

    @cached_property
    def request_unmarshaller_cls(self) -> Optional[RequestUnmarshallerType]:
        if not isinstance(self.config.request_unmarshaller_cls, Unset):
            return self.config.request_unmarshaller_cls
        return REQUEST_UNMARSHALLERS.get(self.version)

    @cached_property
    def response_unmarshaller_cls(self) -> Optional[ResponseUnmarshallerType]:
        if not isinstance(self.config.response_unmarshaller_cls, Unset):
            return self.config.response_unmarshaller_cls
        return RESPONSE_UNMARSHALLERS.get(self.version)

    @cached_property
    def webhook_request_unmarshaller_cls(
        self,
    ) -> Optional[WebhookRequestUnmarshallerType]:
        if not isinstance(self.config.webhook_request_unmarshaller_cls, Unset):
            return self.config.webhook_request_unmarshaller_cls
        return WEBHOOK_REQUEST_UNMARSHALLERS.get(self.version)

    @cached_property
    def webhook_response_unmarshaller_cls(
        self,
    ) -> Optional[WebhookResponseUnmarshallerType]:
        if not isinstance(
            self.config.webhook_response_unmarshaller_cls, Unset
        ):
            return self.config.webhook_response_unmarshaller_cls
        return WEBHOOK_RESPONSE_UNMARSHALLERS.get(self.version)

    @cached_property
    def request_validator(self) -> RequestValidator:
        if self.request_validator_cls is None:
            raise SpecError("Validator class not found")
        return self.request_validator_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
            security_provider_factory=self.config.security_provider_factory,
        )

    @cached_property
    def response_validator(self) -> ResponseValidator:
        if self.response_validator_cls is None:
            raise SpecError("Validator class not found")
        return self.response_validator_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
        )

    @cached_property
    def webhook_request_validator(self) -> WebhookRequestValidator:
        if self.webhook_request_validator_cls is None:
            raise SpecError("Validator class not found")
        return self.webhook_request_validator_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.webhook_path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
            security_provider_factory=self.config.security_provider_factory,
        )

    @cached_property
    def webhook_response_validator(self) -> WebhookResponseValidator:
        if self.webhook_response_validator_cls is None:
            raise SpecError("Validator class not found")
        return self.webhook_response_validator_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.webhook_path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
        )

    @cached_property
    def request_unmarshaller(self) -> RequestUnmarshaller:
        if self.request_unmarshaller_cls is None:
            raise SpecError("Unmarshaller class not found")
        return self.request_unmarshaller_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
            security_provider_factory=self.config.security_provider_factory,
            schema_unmarshallers_factory=self.config.schema_unmarshallers_factory,
            extra_format_unmarshallers=self.config.extra_format_unmarshallers,
        )

    @cached_property
    def response_unmarshaller(self) -> ResponseUnmarshaller:
        if self.response_unmarshaller_cls is None:
            raise SpecError("Unmarshaller class not found")
        return self.response_unmarshaller_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
            schema_unmarshallers_factory=self.config.schema_unmarshallers_factory,
            extra_format_unmarshallers=self.config.extra_format_unmarshallers,
        )

    @cached_property
    def webhook_request_unmarshaller(self) -> WebhookRequestUnmarshaller:
        if self.webhook_request_unmarshaller_cls is None:
            raise SpecError("Unmarshaller class not found")
        return self.webhook_request_unmarshaller_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.webhook_path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
            security_provider_factory=self.config.security_provider_factory,
            schema_unmarshallers_factory=self.config.schema_unmarshallers_factory,
            extra_format_unmarshallers=self.config.extra_format_unmarshallers,
        )

    @cached_property
    def webhook_response_unmarshaller(self) -> WebhookResponseUnmarshaller:
        if self.webhook_response_unmarshaller_cls is None:
            raise SpecError("Unmarshaller class not found")
        return self.webhook_response_unmarshaller_cls(
            self.spec,
            base_url=self.config.server_base_url,
            style_deserializers_factory=self.config.style_deserializers_factory,
            media_type_deserializers_factory=self.config.media_type_deserializers_factory,
            schema_casters_factory=self.config.schema_casters_factory,
            schema_validators_factory=self.config.schema_validators_factory,
            path_finder_cls=self.config.webhook_path_finder_cls,
            spec_validator_cls=self.config.spec_validator_cls,
            extra_format_validators=self.config.extra_format_validators,
            extra_media_type_deserializers=self.config.extra_media_type_deserializers,
            schema_unmarshallers_factory=self.config.schema_unmarshallers_factory,
            extra_format_unmarshallers=self.config.extra_format_unmarshallers,
        )

    def validate_request(
        self,
        request: Annotated[
            AnyRequest,
            Doc(
                """
                Request object to be validated.
                """
            ),
        ],
    ) -> None:
        """Validates the given request object.

        Args:
            request (AnyRequest): Request object to be validated.

        Raises:
            TypeError: If the request object is not of the expected type.
            SpecError: If the validator class is not found.
        """
        if isinstance(request, WebhookRequest):
            self.validate_webhook_request(request)
        else:
            self.validate_apicall_request(request)

    def validate_response(
        self,
        request: Annotated[
            AnyRequest,
            Doc(
                """
                Request object associated with the response.
                """
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                """
                Response object to be validated.
                """
            ),
        ],
    ) -> None:
        """Validates the given response object associated with the request.

        Args:
            request (AnyRequest): Request object associated with the response.
            response (Response): Response object to be validated.

        Raises:
            TypeError: If the request or response object is not of the expected type.
            SpecError: If the validator class is not found.
        """
        if isinstance(request, WebhookRequest):
            self.validate_webhook_response(request, response)
        else:
            self.validate_apicall_response(request, response)

    def validate_apicall_request(
        self,
        request: Annotated[
            Request,
            Doc(
                """
                API call request object to be validated.
                """
            ),
        ],
    ) -> None:
        if not isinstance(request, Request):
            raise TypeError("'request' argument is not type of Request")
        self.request_validator.validate(request)

    def validate_apicall_response(
        self,
        request: Annotated[
            Request,
            Doc(
                """
                API call request object associated with the response.
                """
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                """
                API call response object to be validated.
                """
            ),
        ],
    ) -> None:
        if not isinstance(request, Request):
            raise TypeError("'request' argument is not type of Request")
        if not isinstance(response, Response):
            raise TypeError("'response' argument is not type of Response")
        self.response_validator.validate(request, response)

    def validate_webhook_request(
        self,
        request: Annotated[
            WebhookRequest,
            Doc(
                """
                Webhook request object to be validated.
                """
            ),
        ],
    ) -> None:
        if not isinstance(request, WebhookRequest):
            raise TypeError("'request' argument is not type of WebhookRequest")
        self.webhook_request_validator.validate(request)

    def validate_webhook_response(
        self,
        request: Annotated[
            WebhookRequest,
            Doc(
                """
                Webhook request object associated with the response.
                """
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                """
                Webhook response object to be validated.
                """
            ),
        ],
    ) -> None:
        if not isinstance(request, WebhookRequest):
            raise TypeError("'request' argument is not type of WebhookRequest")
        if not isinstance(response, Response):
            raise TypeError("'response' argument is not type of Response")
        self.webhook_response_validator.validate(request, response)

    def unmarshal_request(
        self,
        request: Annotated[
            AnyRequest,
            Doc(
                """
                Request object to be unmarshalled.
                """
            ),
        ],
    ) -> RequestUnmarshalResult:
        """Unmarshals the given request object.

        Args:
            request (AnyRequest): Request object to be unmarshalled.

        Returns:
            RequestUnmarshalResult: The result of the unmarshalling process.

        Raises:
            TypeError: If the request object is not of the expected type.
            SpecError: If the unmarshaller class is not found.
        """
        if isinstance(request, WebhookRequest):
            return self.unmarshal_webhook_request(request)
        else:
            return self.unmarshal_apicall_request(request)

    def unmarshal_response(
        self,
        request: Annotated[
            AnyRequest,
            Doc(
                """
                Request object associated with the response.
                """
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                """
                Response object to be unmarshalled.
                """
            ),
        ],
    ) -> ResponseUnmarshalResult:
        """Unmarshals the given response object associated with the request.

        Args:
            request (AnyRequest): Request object associated with the response.
            response (Response): Response object to be unmarshalled.

        Returns:
            ResponseUnmarshalResult: The result of the unmarshalling process.

        Raises:
            TypeError: If the request or response object is not of the expected type.
            SpecError: If the unmarshaller class is not found.
        """
        if isinstance(request, WebhookRequest):
            return self.unmarshal_webhook_response(request, response)
        else:
            return self.unmarshal_apicall_response(request, response)

    def unmarshal_apicall_request(
        self,
        request: Annotated[
            Request,
            Doc(
                """
                API call request object to be unmarshalled.
                """
            ),
        ],
    ) -> RequestUnmarshalResult:
        if not isinstance(request, Request):
            raise TypeError("'request' argument is not type of Request")
        return self.request_unmarshaller.unmarshal(request)

    def unmarshal_apicall_response(
        self,
        request: Annotated[
            Request,
            Doc(
                """
                API call request object associated with the response.
                """
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                """
                API call response object to be unmarshalled.
                """
            ),
        ],
    ) -> ResponseUnmarshalResult:
        if not isinstance(request, Request):
            raise TypeError("'request' argument is not type of Request")
        if not isinstance(response, Response):
            raise TypeError("'response' argument is not type of Response")
        return self.response_unmarshaller.unmarshal(request, response)

    def unmarshal_webhook_request(
        self,
        request: Annotated[
            WebhookRequest,
            Doc(
                """
                Webhook request object to be unmarshalled.
                """
            ),
        ],
    ) -> RequestUnmarshalResult:
        if not isinstance(request, WebhookRequest):
            raise TypeError("'request' argument is not type of WebhookRequest")
        return self.webhook_request_unmarshaller.unmarshal(request)

    def unmarshal_webhook_response(
        self,
        request: Annotated[
            WebhookRequest,
            Doc(
                """
                Webhook request object associated with the response.
                """
            ),
        ],
        response: Annotated[
            Response,
            Doc(
                """
                Webhook response object to be unmarshalled.
                """
            ),
        ],
    ) -> ResponseUnmarshalResult:
        if not isinstance(request, WebhookRequest):
            raise TypeError("'request' argument is not type of WebhookRequest")
        if not isinstance(response, Response):
            raise TypeError("'response' argument is not type of Response")
        return self.webhook_response_unmarshaller.unmarshal(request, response)
