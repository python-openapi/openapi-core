# FastAPI

This section describes integration with [FastAPI](https://fastapi.tiangolo.com) ASGI framework.

!!! note

    FastAPI also provides OpenAPI support. The main difference is that, unlike FastAPI's code-first approach, OpenAPI-core allows you to leverage your existing specification that aligns with the API-First approach. You can read more about API-first vs. code-first in the [Guide to API-first](https://www.postman.com/api-first/).

## Middleware

FastAPI can be integrated by [middleware](https://fastapi.tiangolo.com/tutorial/middleware/) to apply OpenAPI validation to your entire application.

Add `FastAPIOpenAPIMiddleware` with the OpenAPI object to your `middleware` list.

``` python hl_lines="2 5"
from fastapi import FastAPI
from openapi_core.contrib.fastapi.middlewares import FastAPIOpenAPIMiddleware

app = FastAPI()
app.add_middleware(FastAPIOpenAPIMiddleware, openapi=openapi)
```

After that, all your requests and responses will be validated.

You also have access to the unmarshal result object with all unmarshalled request data through the `openapi` scope of the request object.

``` python
async def homepage(request):
    # get parameters object with path, query, cookies and headers parameters
    unmarshalled_params = request.scope["openapi"].parameters
    # or specific location parameters
    unmarshalled_path_params = request.scope["openapi"].parameters.path

    # get body
    unmarshalled_body = request.scope["openapi"].body

    # get security data
    unmarshalled_security = request.scope["openapi"].security
```

### Response validation

You can skip the response validation process by setting `response_cls` to `None`

``` python hl_lines="5"
app = FastAPI()
app.add_middleware(
    FastAPIOpenAPIMiddleware,
    openapi=openapi,
    response_cls=None,
)
```

## Low level

For low-level integration, see [Starlette](starlette.md) integration.
