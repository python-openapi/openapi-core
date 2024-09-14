# Response validator

By default, response validator is selected based on detected specification version.

In order to explicitly validate a:

- OpenAPI 3.0 spec, import `V30ResponseValidator`
- OpenAPI 3.1 spec, import `V31ResponseValidator` or `V31WebhookResponseValidator`

``` python hl_lines="1 4"
from openapi_core import V31ResponseValidator

config = Config(
    response_validator_cls=V31ResponseValidator,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)
openapi.validate_response(request, response)
```

You can also explicitly import `V3ResponseValidator`  which is a shortcut to the latest OpenAPI v3 version.
