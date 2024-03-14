from typing import Dict
from typing import List
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


class APIGatewayEventConfig:
    extra = "allow"


@dataclass(config=APIGatewayEventConfig, frozen=True)
class APIGatewayEvent:
    """AWS API Gateway event"""

    headers: Dict[str, str]

    path: str
    httpMethod: str
    resource: str

    queryStringParameters: Optional[Dict[str, str]] = None
    isBase64Encoded: Optional[bool] = None
    body: Optional[str] = None
    pathParameters: Optional[Dict[str, str]] = None
    stageVariables: Optional[Dict[str, str]] = None

    multiValueHeaders: Optional[Dict[str, List[str]]] = None
    version: Optional[str] = "1.0"
    multiValueQueryStringParameters: Optional[Dict[str, List[str]]] = None


@dataclass(config=APIGatewayEventConfig, frozen=True)
class APIGatewayEventV2Http:
    """AWS API Gateway event v2 HTTP"""

    method: str
    path: str


@dataclass(config=APIGatewayEventConfig, frozen=True)
class APIGatewayEventV2:
    """AWS API Gateway event v2"""

    headers: Dict[str, str]

    version: str
    routeKey: str
    rawPath: str
    rawQueryString: str
    http: APIGatewayEventV2Http

    queryStringParameters: Optional[Dict[str, str]] = None
    isBase64Encoded: Optional[bool] = None
    body: Optional[str] = None
    pathParameters: Optional[Dict[str, str]] = None
    stageVariables: Optional[Dict[str, str]] = None

    cookies: Optional[List[str]] = None


@dataclass(config=APIGatewayEventConfig, frozen=True)
class APIGatewayEventResponse:
    """AWS API Gateway event response"""

    body: str
    isBase64Encoded: bool
    statusCode: int
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]]


@dataclass(config=APIGatewayEventConfig, frozen=True)
class APIGatewayEventV2Response:
    """AWS API Gateway event v2 response"""

    body: str
    isBase64Encoded: bool = False
    statusCode: int = 200
    headers: Dict[str, str] = Field(
        default_factory=lambda: {"content-type": "application/json"}
    )
