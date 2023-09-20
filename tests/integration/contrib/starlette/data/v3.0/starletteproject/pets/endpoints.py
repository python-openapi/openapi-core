from base64 import b64decode

from starlette.responses import Response
from starlette.responses import StreamingResponse
from starletteproject.openapi import spec

from openapi_core import unmarshal_request
from openapi_core import unmarshal_response
from openapi_core.contrib.starlette import StarletteOpenAPIRequest
from openapi_core.contrib.starlette import StarletteOpenAPIResponse

OPENID_LOGO = b64decode(
    """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
)


def pet_photo_endpoint(request):
    openapi_request = StarletteOpenAPIRequest(request)
    request_unmarshalled = unmarshal_request(openapi_request, spec=spec)
    if request.method == "GET":
        response = StreamingResponse([OPENID_LOGO], media_type="image/gif")
    elif request.method == "POST":
        with request.form() as form:
            filename = form["file"].filename
            contents = form["file"].read()
            response = Response(status_code=201)
    openapi_response = StarletteOpenAPIResponse(response)
    response_unmarshalled = unmarshal_response(
        openapi_request, openapi_response, spec=spec
    )
    return response
