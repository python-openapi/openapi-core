# Starlette

This section describes integration with the [Starlette](https://www.starlette.io) ASGI framework.

## Middleware

Starlette can be integrated using [middleware](https://www.starlette.io/middleware/) to apply OpenAPI validation to your entire application.

Add `StarletteOpenAPIMiddleware` with the OpenAPI object to your `middleware` list.

``` python hl_lines="1 6"
from openapi_core.contrib.starlette.middlewares import StarletteOpenAPIMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware

middleware = [
    Middleware(StarletteOpenAPIMiddleware, openapi=openapi),
]

app = Starlette(
    # ...
    middleware=middleware,
)
```

After that, all your requests and responses will be validated.

You also have access to the unmarshalled result object with all unmarshalled request data through the `openapi` scope of the request object.

``` python
async def homepage(request):
    # get parameters object with path, query, cookies, and headers parameters
    unmarshalled_params = request.scope["openapi"].parameters
    # or specific location parameters
    unmarshalled_path_params = request.scope["openapi"].parameters.path

    # get body
    unmarshalled_body = request.scope["openapi"].body

    # get security data
    unmarshalled_security = request.scope["openapi"].security
```

### Response validation

You can skip the response validation process by setting `response_cls` to `None`.

``` python hl_lines="2"
middleware = [
    Middleware(StarletteOpenAPIMiddleware, openapi=openapi, response_cls=None),
]

app = Starlette(
    # ...
    middleware=middleware,
)
```

## Low level

The integration defines classes useful for low-level integration.

### Request

Use `StarletteOpenAPIRequest` to create an OpenAPI request from a Starlette request:

``` python
from openapi_core.contrib.starlette import StarletteOpenAPIRequest

async def homepage(request):
    openapi_request = StarletteOpenAPIRequest(request)
    result = openapi.unmarshal_request(openapi_request)
    return JSONResponse({'hello': 'world'})
```

### Response

Use `StarletteOpenAPIResponse` to create an OpenAPI response from a Starlette response:

``` python
from openapi_core.contrib.starlette import StarletteOpenAPIResponse

async def homepage(request):
    response = JSONResponse({'hello': 'world'})
    openapi_request = StarletteOpenAPIRequest(request)
    openapi_response = StarletteOpenAPIResponse(response)
    openapi.validate_response(openapi_request, openapi_response)
    return response
```
