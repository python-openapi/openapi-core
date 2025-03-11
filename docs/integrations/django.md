# Django

This section describes the integration with the [Django](https://www.djangoproject.com) web framework.
The integration supports Django version 3.0 and above.

## Middleware

Django can be integrated using [middleware](https://docs.djangoproject.com/en/5.0/topics/http/middleware/) to apply OpenAPI validation to your entire application.

Add `DjangoOpenAPIMiddleware` to your `MIDDLEWARE` list and define `OPENAPI`.

``` python hl_lines="5 8" title="settings.py"
from openapi_core import OpenAPI

MIDDLEWARE = [
    # ...
    'openapi_core.contrib.django.middlewares.DjangoOpenAPIMiddleware',
]

OPENAPI = OpenAPI.from_dict(spec_dict)
```

After that, all your requests and responses will be validated.

You also have access to the unmarshalled result object with all unmarshalled request data through the `openapi` attribute of the request object.

``` python
from django.views import View

class MyView(View):
    def get(self, request):
        # Get parameters object with path, query, cookies, and headers parameters
        unmarshalled_params = request.openapi.parameters
        # Or specific location parameters
        unmarshalled_path_params = request.openapi.parameters.path

        # Get body
        unmarshalled_body = request.openapi.body

        # Get security data
        unmarshalled_security = request.openapi.security
```

### Response validation

You can skip the response validation process by setting `OPENAPI_RESPONSE_CLS` to `None`.

``` python hl_lines="9" title="settings.py"
from openapi_core import OpenAPI

MIDDLEWARE = [
    # ...
    'openapi_core.contrib.django.middlewares.DjangoOpenAPIMiddleware',
]

OPENAPI = OpenAPI.from_dict(spec_dict)
OPENAPI_RESPONSE_CLS = None
```

## Low level

The integration defines classes useful for low-level integration.

### Request

Use `DjangoOpenAPIRequest` to create an OpenAPI request from a Django request:

``` python
from openapi_core.contrib.django import DjangoOpenAPIRequest

class MyView(View):
    def get(self, request):
        openapi_request = DjangoOpenAPIRequest(request)
        openapi.validate_request(openapi_request)
```

### Response

Use `DjangoOpenAPIResponse` to create an OpenAPI response from a Django response:

``` python
from openapi_core.contrib.django import DjangoOpenAPIResponse

class MyView(View):
    def get(self, request):
        response = JsonResponse({'hello': 'world'})
        openapi_request = DjangoOpenAPIRequest(request)
        openapi_response = DjangoOpenAPIResponse(response)
        openapi.validate_response(openapi_request, openapi_response)
        return response
```
