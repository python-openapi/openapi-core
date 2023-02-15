"""OpenAPI core validation processors module"""
from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.spec import Spec
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.proxies import (
    SpecRequestValidatorProxy,
)
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.proxies import (
    SpecResponseValidatorProxy,
)


class OpenAPISpecProcessor:
    def __init__(
        self,
        request_unmarshaller: SpecRequestValidatorProxy,
        response_unmarshaller: SpecResponseValidatorProxy,
    ):
        self.request_unmarshaller = request_unmarshaller
        self.response_unmarshaller = response_unmarshaller

    def process_request(
        self, spec: Spec, request: Request
    ) -> RequestUnmarshalResult:
        return self.request_unmarshaller.validate(spec, request)

    def process_response(
        self, spec: Spec, request: Request, response: Response
    ) -> ResponseUnmarshalResult:
        return self.response_unmarshaller.validate(spec, request, response)
