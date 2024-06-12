from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

API_GATEWAY_EVENT_CONFIG = dict(extra="allow")


@dataclass(frozen=True)
class APIGatewayEventRequestContext:
    """AWS API Gateway event request context"""
    model_config = API_GATEWAY_EVENT_CONFIG

    resourceId: str


@dataclass(frozen=True)
class APIGatewayEvent:
    """AWS API Gateway event"""
    model_config = API_GATEWAY_EVENT_CONFIG

    headers: Dict[str, str]

    path: str
    httpMethod: str
    resource: str
    requestContext: APIGatewayEventRequestContext

    queryStringParameters: Optional[Dict[str, str]] = None
    isBase64Encoded: Optional[bool] = None
    body: Optional[str] = None
    pathParameters: Optional[Dict[str, str]] = None
    stageVariables: Optional[Dict[str, str]] = None

    multiValueHeaders: Optional[Dict[str, List[str]]] = None
    version: Optional[str] = "1.0"
    multiValueQueryStringParameters: Optional[Dict[str, List[str]]] = None


@dataclass(frozen=True)
class APIGatewayEventV2Http:
    """AWS API Gateway event v2 HTTP"""
    model_config = API_GATEWAY_EVENT_CONFIG

    method: str
    path: str


@dataclass(frozen=True)
class APIGatewayEventV2RequestContext:
    """AWS API Gateway event v2 request context"""
    model_config = API_GATEWAY_EVENT_CONFIG

    http: APIGatewayEventV2Http


@dataclass(frozen=True)
class APIGatewayEventV2:
    """AWS API Gateway event v2"""
    model_config = API_GATEWAY_EVENT_CONFIG

    headers: Dict[str, str]

    version: Literal["2.0"]
    routeKey: str
    rawPath: str
    rawQueryString: str
    requestContext: APIGatewayEventV2RequestContext

    queryStringParameters: Optional[Dict[str, str]] = None
    isBase64Encoded: Optional[bool] = None
    body: Optional[str] = None
    pathParameters: Optional[Dict[str, str]] = None
    stageVariables: Optional[Dict[str, str]] = None

    cookies: Optional[List[str]] = None


@dataclass(frozen=True)
class APIGatewayEventResponse:
    """AWS API Gateway event response"""
    model_config = API_GATEWAY_EVENT_CONFIG

    body: str
    isBase64Encoded: bool
    statusCode: int
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]]


@dataclass(frozen=True)
class APIGatewayEventV2Response:
    """AWS API Gateway event v2 response"""
    model_config = API_GATEWAY_EVENT_CONFIG

    body: str
    isBase64Encoded: bool = False
    statusCode: int = 200
    headers: Dict[str, str] = Field(
        default_factory=lambda: {"content-type": "application/json"}
    )
