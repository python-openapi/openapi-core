from base64 import b64decode
from io import BytesIO

from aiohttp import web
from aiohttpproject.openapi import openapi
from multidict import MultiDict

from openapi_core import unmarshal_request
from openapi_core import unmarshal_response
from openapi_core.contrib.aiohttp import AIOHTTPOpenAPIWebRequest
from openapi_core.contrib.aiohttp import AIOHTTPOpenAPIWebResponse


class PetPhotoView(web.View):
    OPENID_LOGO = b64decode(
        """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
    )

    async def get(self):
        request_body = await self.request.text()
        openapi_request = AIOHTTPOpenAPIWebRequest(
            self.request, body=request_body
        )
        request_unmarshalled = openapi.unmarshal_request(openapi_request)
        response = web.Response(
            body=self.OPENID_LOGO,
            content_type="image/gif",
        )
        openapi_response = AIOHTTPOpenAPIWebResponse(response)
        response_unmarshalled = openapi.unmarshal_response(
            openapi_request, openapi_response
        )
        return response

    async def post(self):
        request_body = await self.request.read()
        openapi_request = AIOHTTPOpenAPIWebRequest(
            self.request, body=request_body
        )
        request_unmarshalled = openapi.unmarshal_request(openapi_request)
        response = web.Response(status=201)
        openapi_response = AIOHTTPOpenAPIWebResponse(response)
        response_unmarshalled = openapi.unmarshal_response(
            openapi_request, openapi_response
        )
        return response
