---
hide:
  - navigation
---

# Unmarshalling

Unmarshalling is the process of converting a primitive schema type of value into a higher-level object based on a `format` keyword. All request/response data, that can be described by a schema in OpenAPI specification, can be unmarshalled.

Unmarshallers firstly validate data against the provided schema (See [Validation](validation.md)).

Openapi-core comes with a set of built-in format unmarshallers:

- `date` - converts string into a date object,
- `date-time` - converts string into a datetime object,
- `binary` - converts string into a byte object,
- `uuid` - converts string into an UUID object,
- `byte` - decodes Base64-encoded string.

You can also define your own format unmarshallers (See [Format unmarshallers](customizations/extra_format_unmarshallers.md)).

## Request unmarshalling

Use `unmarshal_request` method to validate and unmarshal request data against a given spec. By default, OpenAPI spec version is detected:

```python
# raises error if request is invalid
result = openapi.unmarshal_request(request)
```

Request object should implement OpenAPI Request protocol (See [Integrations](integrations/index.md)).

!!! note

    Webhooks feature is part of OpenAPI v3.1 only


Use the same method to validate and unmarshal webhook request data against a given spec.

```python
# raises error if request is invalid
result = openapi.unmarshal_request(webhook_request)
```

Webhook request object should implement OpenAPI WebhookRequest protocol (See [Integrations](integrations/index.md)).

Retrieve validated and unmarshalled request data

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

You can also define your own request unmarshaller (See [Request unmarshaller](customizations/request_unmarshaller_cls.md)).

## Response unmarshalling

Use `unmarshal_response` method to validate and unmarshal response data against a given spec. By default, OpenAPI spec version is detected:

```python
# raises error if response is invalid
result = openapi.unmarshal_response(request, response)
```

Response object should implement OpenAPI Response protocol  (See [Integrations](integrations/index.md)).

!!! note

    Webhooks feature is part of OpenAPI v3.1 only

Use the same method to validate and unmarshal response data from webhook request against a given spec.

```python
# raises error if request is invalid
result = openapi.unmarshal_response(webhook_request, response)
```

Retrieve validated and unmarshalled response data

```python
# get headers
headers = result.headers
# get data
data = result.data
```

You can also define your own response unmarshaller (See [Response unmarshaller](customizations/response_unmarshaller_cls.md)).
