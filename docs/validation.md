---
hide:
  - navigation
---

# Validation

Validation is a process to validate request/response data under a given schema defined in the OpenAPI specification.

Additionally, openapi-core uses the `format` keyword to check if primitive types conform to defined formats.

Such valid formats can be further unmarshalled (See [Unmarshalling](unmarshalling.md)).

Depending on the OpenAPI version, openapi-core comes with a set of built-in format validators such as: `date`, `date-time`, `binary`, `uuid`, or `byte`.

You can also define your own format validators (See [Extra Format Validators](configuration.md#extra-format-validators)).

## Request validation

Use the `validate_request` method to validate request data against a given spec. By default, the OpenAPI spec version is detected:

```python
# raises error if request is invalid
openapi.validate_request(request)
```

The request object should implement the OpenAPI Request protocol (See [Integrations](integrations/index.md)).

!!! note

    The Webhooks feature is part of OpenAPI v3.1 only

Use the same method to validate webhook request data against a given spec.

```python
# raises error if request is invalid
openapi.validate_request(webhook_request)
```

The webhook request object should implement the OpenAPI WebhookRequest protocol (See [Integrations](integrations/index.md)).

You can also define your own request validator (See [Request Validator](configuration.md#request-validator)).

## Response validation

Use the `validate_response` function to validate response data against a given spec. By default, the OpenAPI spec version is detected:

```python
from openapi_core import validate_response

# raises error if response is invalid
openapi.validate_response(request, response)
```

The response object should implement the OpenAPI Response protocol (See [Integrations](integrations/index.md)).

!!! note

    The Webhooks feature is part of OpenAPI v3.1 only

Use the same function to validate response data from a webhook request against a given spec.

```python
# raises error if request is invalid
openapi.validate_response(webhook_request, response)
```

You can also define your own response validator (See [Response Validator](configuration.md#response-validator)).
