from typing import Any

from openapi_core.validation.response.datatypes import OpenAPIResponse


class BaseOpenAPIResponseFactory:

    def create(self, response: Any) -> OpenAPIResponse:
        raise NotImplementedError
