# Specification validation

By default, on OpenAPI creation time, the provided specification is also validated.

If you know you have a valid specification already, disabling the validator can improve the performance.

``` python hl_lines="1 4 6"
from openapi_core import Config

config = Config(
    spec_validator_cls=None,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)
```
