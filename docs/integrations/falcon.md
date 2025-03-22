# Falcon

This section describes integration with [Falcon](https://falconframework.org) web framework.
The integration supports Falcon from version 3.0 and above.

!!! warning

    This integration does not support multipart form body requests.

## Middleware

The Falcon API can be integrated by `FalconOpenAPIMiddleware` middleware.

``` python hl_lines="1 3 7"
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

openapi_middleware = FalconOpenAPIMiddleware.from_spec(spec)

app = falcon.App(
    # ...
    middleware=[openapi_middleware],
)
```

Additional customization parameters can be passed to the middleware.

``` python hl_lines="5"
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

openapi_middleware = FalconOpenAPIMiddleware.from_spec(
    spec,
    extra_format_validators=extra_format_validators,
)

app = falcon.App(
    # ...
    middleware=[openapi_middleware],
)
```

You can skip response validation process: by setting `response_cls` to `None`

``` python hl_lines="5"
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

openapi_middleware = FalconOpenAPIMiddleware.from_spec(
    spec,
    response_cls=None,
)

app = falcon.App(
    # ...
    middleware=[openapi_middleware],
)
```

After that you will have access to validation result object with all validated request data from Falcon view through request context.

``` python
class ThingsResource:
    def on_get(self, req, resp):
        # get parameters object with path, query, cookies and headers parameters
        validated_params = req.context.openapi.parameters
        # or specific location parameters
        validated_path_params = req.context.openapi.parameters.path

        # get body
        validated_body = req.context.openapi.body

        # get security data
        validated_security = req.context.openapi.security
```

## Low level

You can use `FalconOpenAPIRequest` as a Falcon request factory:

``` python
from openapi_core.contrib.falcon import FalconOpenAPIRequest

openapi_request = FalconOpenAPIRequest(falcon_request)
result = openapi.unmarshal_request(openapi_request)
```

You can use `FalconOpenAPIResponse` as a Falcon response factory:

``` python
from openapi_core.contrib.falcon import FalconOpenAPIResponse

openapi_response = FalconOpenAPIResponse(falcon_response)
result = openapi.unmarshal_response(openapi_request, openapi_response)
```
