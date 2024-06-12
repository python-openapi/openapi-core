from typing import Dict
from typing import Optional
from typing import Tuple
from urllib.parse import urljoin

from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableMultiDict

from openapi_core.contrib.aws.datatypes import APIGatewayEvent
from openapi_core.contrib.aws.datatypes import APIGatewayEventV2
from openapi_core.contrib.aws.types import APIGatewayEventPayload
from openapi_core.contrib.aws.util import parse_forwarded
from openapi_core.datatypes import RequestParameters


class APIGatewayAWSProxyOpenAPIRequest:
    """
    API Gateway AWS proxy event payload OpenAPI request.

    Designed to be used with API Gateway REST API specification exports for
    integrations that use event v1 payload. Uses API Gateway event v1
    requestContext's resourceId. Requires APIGatewayPathFinder to resolve ANY methods.
    """

    def __init__(self, payload: APIGatewayEventPayload):
        self.event = APIGatewayEvent(**payload)

        self.parameters = RequestParameters(
            path=self.path_params,
            query=ImmutableMultiDict(self.query_params),
            header=Headers(self.event.headers),
            cookie=ImmutableMultiDict(),
        )

    @property
    def resource_id(self) -> Tuple[str, str]:
        return self.event.requestContext.resourceId.split(" ")

    @property
    def path_params(self) -> Dict[str, str]:
        params = self.event.pathParameters
        if params is None:
            return {}
        return params

    @property
    def query_params(self) -> Dict[str, str]:
        params = self.event.queryStringParameters
        if params is None:
            return {}
        return params

    @property
    def proto(self) -> str:
        return self.event.headers.get("X-Forwarded-Proto", "https")

    @property
    def host(self) -> str:
        return self.event.headers["Host"]

    @property
    def host_url(self) -> str:
        return "://".join([self.proto, self.host])

    @property
    def path(self) -> str:
        return self.event.path

    @property
    def method(self) -> str:
        return self.resource_id[0].lower()

    @property
    def body(self) -> Optional[str]:
        return self.event.body

    @property
    def content_type(self) -> str:
        return self.event.headers.get("Content-Type", "")

    @property
    def path_pattern(self):
        return self.resource_id[1]


class APIGatewayAWSProxyV2OpenAPIRequest:
    """
    API Gateway AWS Proxy event v2 payload OpenAPI request.

    Designed to be used with API Gateway HTTP API specification exports for
    integrations that use event v2 payload. Uses API Gateway event v2 routeKey
    and rawPath data. Requires APIGatewayPathFinder to resolve ANY methods.

    .. note::
       API Gateway HTTP APIs don't support request validation
    """

    def __init__(self, payload: APIGatewayEventPayload):
        self.event = APIGatewayEventV2(**payload)

        self.parameters = RequestParameters(
            path=self.path_params,
            query=ImmutableMultiDict(self.query_params),
            header=Headers(self.event.headers),
            cookie=ImmutableMultiDict(),
        )

    @property
    def path_params(self) -> Dict[str, str]:
        if self.event.pathParameters is None:
            return {}
        return self.event.pathParameters

    @property
    def query_params(self) -> Dict[str, str]:
        if self.event.queryStringParameters is None:
            return {}
        return self.event.queryStringParameters

    @property
    def proto(self) -> str:
        return self.event.headers.get("x-forwarded-proto", "https")

    @property
    def host(self) -> str:
        # use Forwarded header if available
        if "forwarded" in self.event.headers:
            forwarded = parse_forwarded(self.event.headers["forwarded"])
            if "host" in forwarded:
                return forwarded["host"]
        return self.event.headers["host"]

    @property
    def host_url(self) -> str:
        return "://".join([self.proto, self.host])

    @property
    def path(self) -> str:
        return self.event.rawPath

    @property
    def method(self) -> str:
        return self.event.routeKey.split(" ")[0].lower()

    @property
    def body(self) -> Optional[str]:
        return self.event.body

    @property
    def content_type(self) -> str:
        return self.event.headers.get("content-type", "")


class APIGatewayHTTPProxyOpenAPIRequest(APIGatewayAWSProxyV2OpenAPIRequest):
    """
    API Gateway HTTP proxy integration event payload OpenAPI request.

    Uses http integration path and method data.

    NOTE: If you use HTTP integration not in root path then you need to provide the base path
    otherwise it won't find the correct path because it is not send with event.
    """

    def __init__(self, payload: APIGatewayEventPayload, base_path: str = "/"):
        super().__init__(payload)
        self.base_path = base_path

    @property
    def path(self) -> str:
        return urljoin(self.base_path, self.event.requestContext.http.path.lstrip('/'))

    @property
    def method(self) -> str:
        return self.event.requestContext.http.method.lower()
