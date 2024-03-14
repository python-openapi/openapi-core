from json import dumps
from typing import Union

from werkzeug.datastructures import Headers

from openapi_core.contrib.aws.datatypes import APIGatewayEventResponse
from openapi_core.contrib.aws.datatypes import APIGatewayEventV2Response
from openapi_core.contrib.aws.types import APIGatewayEventResponsePayload


class APIGatewayEventResponseOpenAPIResponse:
    """
    Converts an API Gateway event response payload to an OpenAPI request
    """

    def __init__(self, payload: APIGatewayEventResponsePayload):
        self.response = APIGatewayEventResponse(**payload)

    @property
    def data(self) -> str:
        return self.response.body

    @property
    def status_code(self) -> int:
        return self.response.statusCode

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers)

    @property
    def mimetype(self) -> str:
        content_type = self.response.headers.get("Content-Type", "")
        assert isinstance(content_type, str)
        return content_type


class APIGatewayEventV2ResponseOpenAPIResponse:
    """
    Converts an API Gateway event v2 response payload to an OpenAPI request
    """

    def __init__(self, payload: Union[APIGatewayEventResponsePayload, str]):
        if not isinstance(payload, dict):
            payload = self._construct_payload(payload)
        elif "statusCode" not in payload:
            body = dumps(payload)
            payload = self._construct_payload(body)

        self.response = APIGatewayEventV2Response(**payload)

    @staticmethod
    def _construct_payload(body: str) -> APIGatewayEventResponsePayload:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "content-type": "application/json",
            },
            "body": body,
        }

    @property
    def data(self) -> str:
        return self.response.body

    @property
    def status_code(self) -> int:
        return self.response.statusCode

    @property
    def headers(self) -> Headers:
        return Headers(self.response.headers)

    @property
    def mimetype(self) -> str:
        content_type = self.response.headers.get(
            "content-type", "application/json"
        )
        assert isinstance(content_type, str)
        return content_type
