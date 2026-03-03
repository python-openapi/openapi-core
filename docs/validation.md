---
hide:
  - navigation
---

# Validation

Validation is a process to validate request/response data under a given schema defined in the OpenAPI specification.

Additionally, openapi-core uses the `format` keyword to check if primitive types conform to defined formats.

Such valid formats can be further unmarshalled (See [Unmarshalling](unmarshalling.md)).

Depending on the OpenAPI version, openapi-core comes with a set of built-in format validators such as: `date`, `date-time`, `binary`, `uuid`, or `byte`.

!!! note

    For backward compatibility, OpenAPI 3.1 validation in openapi-core currently accepts OpenAPI 3.0-style format checker behavior, including `byte` and `binary`.

You can also define your own format validators (See [Extra Format Validators](configuration.md#extra-format-validators)).

## Request validation

Use the `validate_request` method to validate request data against a given spec. By default, the OpenAPI spec version is detected:

```python
# raises error if request is invalid
openapi.validate_request(request)
```

The request object should implement the OpenAPI Request protocol (See [Integrations](integrations/index.md)).

!!! note

    The Webhooks feature is part of OpenAPI v3.1+

Use the same method to validate webhook request data against a given spec.

```python
# raises error if request is invalid
openapi.validate_request(webhook_request)
```

The webhook request object should implement the OpenAPI WebhookRequest protocol (See [Integrations](integrations/index.md)).

You can also define your own request validator (See [Request Validator](configuration.md#request-validator)).

### Iterating request errors

If you want to collect errors instead of raising on the first one, use iterator-based APIs:

```python
errors = list(openapi.iter_request_errors(request))
if errors:
    for error in errors:
        print(type(error), str(error))
```

You can also call `iter_errors` directly on a validator class:

```python
from openapi_core import V31RequestValidator

errors = list(V31RequestValidator(spec).iter_errors(request))
```

Some high-level errors wrap detailed schema errors. To access nested schema details:

```python
for error in openapi.iter_request_errors(request):
    cause = getattr(error, "__cause__", None)
    schema_errors = getattr(cause, "schema_errors", None)
    if schema_errors:
        for schema_error in schema_errors:
            print(schema_error.message)
```

## Response validation

Use the `validate_response` function to validate response data against a given spec. By default, the OpenAPI spec version is detected:

```python
# raises error if response is invalid
openapi.validate_response(request, response)
```

The response object should implement the OpenAPI Response protocol (See [Integrations](integrations/index.md)).

!!! note

    The Webhooks feature is part of OpenAPI v3.1+

Use the same function to validate response data from a webhook request against a given spec.

```python
# raises error if request is invalid
openapi.validate_response(webhook_request, response)
```

You can also define your own response validator (See [Response Validator](configuration.md#response-validator)).

### Iterating response errors

Use `iter_response_errors` to collect validation errors for a response:

```python
errors = list(openapi.iter_response_errors(request, response))
```
