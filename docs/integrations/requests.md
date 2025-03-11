# Requests

This section describes the integration with the [Requests](https://requests.readthedocs.io) library.

## Low level

The integration defines classes useful for low-level integration.

### Request

Use `RequestsOpenAPIRequest` to create an OpenAPI request from a Requests request:

``` python
from requests import Request, Session
from openapi_core.contrib.requests import RequestsOpenAPIRequest

request = Request('POST', url, data=data, headers=headers)
openapi_request = RequestsOpenAPIRequest(request)
openapi.validate_request(openapi_request)
```

### Webhook request

Use `RequestsOpenAPIWebhookRequest` to create an OpenAPI webhook request from a Requests request:

``` python
from requests import Request, Session
from openapi_core.contrib.requests import RequestsOpenAPIWebhookRequest

request = Request('POST', url, data=data, headers=headers)
openapi_webhook_request = RequestsOpenAPIWebhookRequest(request, "my_webhook")
openapi.validate_request(openapi_webhook_request)
```

### Response

Use `RequestsOpenAPIResponse` to create an OpenAPI response from a Requests response:

``` python
from requests import Request, Session
from openapi_core.contrib.requests import RequestsOpenAPIResponse

session = Session()
request = Request('POST', url, data=data, headers=headers)
prepped = session.prepare_request(request)
response = session.send(prepped)
openapi_request = RequestsOpenAPIRequest(request)
openapi_response = RequestsOpenAPIResponse(response)
openapi.validate_response(openapi_request, openapi_response)
```
