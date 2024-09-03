# Request validator

By default, request validator is selected based on detected specification version.

In order to explicitly validate a:

- OpenAPI 3.0 spec, import `V30RequestValidator`
- OpenAPI 3.1 spec, import `V31RequestValidator` or `V31WebhookRequestValidator`

``` python hl_lines="1 4"
from openapi_core import V31RequestValidator

config = Config(
    request_validator_cls=V31RequestValidator,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)
openapi.validate_request(request)
```

You can also explicitly import `V3RequestValidator` which is a shortcut to the latest OpenAPI v3 version.
