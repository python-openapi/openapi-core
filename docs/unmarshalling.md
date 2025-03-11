---
hide:
  - navigation
---

# Unmarshalling

Unmarshalling is the process of converting a primitive schema type value into a higher-level object based on a `format` keyword. All request/response data that can be described by a schema in the OpenAPI specification can be unmarshalled.

Unmarshallers first validate data against the provided schema (See [Validation](validation.md)).

Openapi-core comes with a set of built-in format unmarshallers:

- `date` - converts a string into a date object,
- `date-time` - converts a string into a datetime object,
- `binary` - converts a string into a byte object,
- `uuid` - converts a string into a UUID object,
- `byte` - decodes a Base64-encoded string.

You can also define your own format unmarshallers (See [Extra Format Unmarshallers](configuration.md#extra-format-unmarshallers)).

## Request unmarshalling

Use the `unmarshal_request` method to validate and unmarshal request data against a given spec. By default, the OpenAPI spec version is detected:

```python
# raises an error if the request is invalid
result = openapi.unmarshal_request(request)
```

The request object should implement the OpenAPI Request protocol (See [Integrations](integrations/index.md)).

!!! note

    The Webhooks feature is part of OpenAPI v3.1 only.

Use the same method to validate and unmarshal webhook request data against a given spec.

```python
# raises an error if the request is invalid
result = openapi.unmarshal_request(webhook_request)
```

The webhook request object should implement the OpenAPI WebhookRequest protocol (See [Integrations](integrations/index.md)).

Retrieve validated and unmarshalled request data:

```python
# get parameters
path_params = result.parameters.path
query_params = result.parameters.query
cookies_params = result.parameters.cookies
headers_params = result.parameters.headers
# get body
body = result.body
# get security data
security = result.security
```

You can also define your own request unmarshaller (See [Request Unmarshaller](configuration.md#request-unmarshaller)).

## Response unmarshalling

Use the `unmarshal_response` method to validate and unmarshal response data against a given spec. By default, the OpenAPI spec version is detected:

```python
# raises an error if the response is invalid
result = openapi.unmarshal_response(request, response)
```

The response object should implement the OpenAPI Response protocol (See [Integrations](integrations/index.md)).

!!! note

    The Webhooks feature is part of OpenAPI v3.1 only.

Use the same method to validate and unmarshal response data from a webhook request against a given spec.

```python
# raises an error if the request is invalid
result = openapi.unmarshal_response(webhook_request, response)
```

Retrieve validated and unmarshalled response data:

```python
# get headers
headers = result.headers
# get data
data = result.data
```

You can also define your own response unmarshaller (See [Response Unmarshaller](configuration.md#response-unmarshaller)).
