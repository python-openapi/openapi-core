# aiohttp.web

This section describes integration with [aiohttp.web](https://docs.aiohttp.org/en/stable/web.html) framework.

## Low level

The integration defines classes useful for low level integration.

### Request

Use `AIOHTTPOpenAPIWebRequest` to create OpenAPI request from aiohttp.web request:

``` python
from openapi_core.contrib.aiohttp import AIOHTTPOpenAPIWebRequest

async def hello(request):
    request_body = await request.text()
    openapi_request = AIOHTTPOpenAPIWebRequest(request, body=request_body)
    openapi.validate_request(openapi_request)
    return web.Response(text="Hello, world")
```

### Response

Use `AIOHTTPOpenAPIWebResponse` to create OpenAPI response from aiohttp.web response:

``` python
from openapi_core.contrib.starlette import AIOHTTPOpenAPIWebResponse

async def hello(request):
    request_body = await request.text()
    response = web.Response(text="Hello, world")
    openapi_request = AIOHTTPOpenAPIWebRequest(request, body=request_body)
    openapi_response = AIOHTTPOpenAPIWebResponse(response)
    result = openapi.unmarshal_response(openapi_request, openapi_response)
    return response
```
