---
hide:
  - navigation
---

# Configuration

OpenAPI accepts a `Config` object that allows users to customize the behavior of validation and unmarshalling processes.

## Specification Validation

By default, when creating an OpenAPI instance, the provided specification is also validated.

If you know that you have a valid specification already, disabling the validator can improve performance.

``` python hl_lines="1 4 6"
from openapi_core import Config

config = Config(
    spec_validator_cls=None,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)
```

## Request Validator

By default, the request validator is selected based on the detected specification version.

To explicitly validate a:

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

You can also explicitly import `V3RequestValidator`, which is a shortcut to the latest OpenAPI v3 version.

## Response Validator

By default, the response validator is selected based on the detected specification version.

To explicitly validate a:

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

You can also explicitly import `V3ResponseValidator`, which is a shortcut to the latest OpenAPI v3 version.

## Request Unmarshaller

By default, the request unmarshaller is selected based on the detected specification version.

To explicitly validate and unmarshal a request for:

- OpenAPI 3.0 spec, import `V30RequestUnmarshaller`
- OpenAPI 3.1 spec, import `V31RequestUnmarshaller` or `V31WebhookRequestUnmarshaller`

``` python hl_lines="1 4"
from openapi_core import V31RequestUnmarshaller

config = Config(
    request_unmarshaller_cls=V31RequestUnmarshaller,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)
result = openapi.unmarshal_request(request)
```

You can also explicitly import `V3RequestUnmarshaller`, which is a shortcut to the latest OpenAPI v3 version.

## Response Unmarshaller

To explicitly validate and unmarshal a response:

- For OpenAPI 3.0 spec, import `V30ResponseUnmarshaller`
- For OpenAPI 3.1 spec, import `V31ResponseUnmarshaller` or `V31WebhookResponseUnmarshaller`

``` python hl_lines="1 4"
from openapi_core import V31ResponseUnmarshaller

config = Config(
    response_unmarshaller_cls=V31ResponseUnmarshaller,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)
result = openapi.unmarshal_response(request, response)
```

You can also explicitly import `V3ResponseUnmarshaller`, which is a shortcut to the latest OpenAPI v3 version.

## Extra Media Type Deserializers

The library comes with a set of built-in media type deserializers for formats such as `application/json`, `application/xml`, `application/x-www-form-urlencoded`, and `multipart/form-data`.

You can also define your own deserializers. To do this, pass a dictionary of custom media type deserializers with the supported MIME types as keys to the `unmarshal_response` function:

```python hl_lines="11"
def protobuf_deserializer(message):
    feature = route_guide_pb2.Feature()
    feature.ParseFromString(message)
    return feature

extra_media_type_deserializers = {
    'application/protobuf': protobuf_deserializer,
}

config = Config(
    extra_media_type_deserializers=extra_media_type_deserializers,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)

result = openapi.unmarshal_response(request, response)
```

## Extra Format Validators

OpenAPI defines a `format` keyword that hints at how a value should be interpreted. For example, a `string` with the format `date` should conform to the RFC 3339 date format.

OpenAPI comes with a set of built-in format validators, but it's also possible to add custom ones.

Here's how you can add support for a `usdate` format that handles dates in the form MM/DD/YYYY:

``` python hl_lines="11"
import re

def validate_usdate(value):
    return bool(re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", value))

extra_format_validators = {
    'usdate': validate_usdate,
}

config = Config(
    extra_format_validators=extra_format_validators,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)

openapi.validate_response(request, response)
```

## Extra Format Unmarshallers

Based on the `format` keyword, openapi-core can also unmarshal values to specific formats.

The library comes with a set of built-in format unmarshallers, but it's also possible to add custom ones.

Here's an example with the `usdate` format that converts a value to a date object:

``` python hl_lines="11"
from datetime import datetime

def unmarshal_usdate(value):
    return datetime.strptime(value, "%m/%d/%Y").date()

extra_format_unmarshallers = {
    'usdate': unmarshal_usdate,
}

config = Config(
    extra_format_unmarshallers=extra_format_unmarshallers,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)

result = openapi.unmarshal_response(request, response)
```
