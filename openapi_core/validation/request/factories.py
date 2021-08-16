from typing import Any

from openapi_core.validation.request.datatypes import OpenAPIRequest


class BaseOpenAPIRequestFactory:

    def create(self, request: Any) -> OpenAPIRequest:
        raise NotImplementedError
