# Werkzeug

This section describes the integration with [Werkzeug](https://werkzeug.palletsprojects.com), a WSGI web application library.

## Low level

The integration defines classes useful for low-level integration.

### Request

Use `WerkzeugOpenAPIRequest` to create an OpenAPI request from a Werkzeug request:

``` python
from openapi_core.contrib.werkzeug import WerkzeugOpenAPIRequest

def application(environ, start_response):
    request = Request(environ)
    openapi_request = WerkzeugOpenAPIRequest(request)
    openapi.validate_request(openapi_request)
    response = Response("Hello world", mimetype='text/plain')
    return response(environ, start_response)
```

### Response

Use `WerkzeugOpenAPIResponse` to create an OpenAPI response from a Werkzeug response:

``` python
from openapi_core.contrib.werkzeug import WerkzeugOpenAPIResponse

def application(environ, start_response):
    request = Request(environ)
    response = Response("Hello world", mimetype='text/plain')
    openapi_request = WerkzeugOpenAPIRequest(request)
    openapi_response = WerkzeugOpenAPIResponse(response)
    openapi.validate_response(openapi_request, openapi_response)
    return response(environ, start_response)
```
