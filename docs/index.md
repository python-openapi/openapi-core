---
hide:
  - navigation
---

# openapi-core

Openapi-core is a Python library that provides client-side and server-side support
for the [OpenAPI v3.0](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md)
and [OpenAPI v3.1](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md) specifications.

## Key features

- [Validation](validation.md) and [Unmarshalling](unmarshalling.md) of request and response data (including webhooks)
- [Integrations](integrations/index.md) with popular libraries (Requests, Werkzeug) and frameworks (Django, Falcon, Flask, Starlette)
- [Configuration](configuration.md) with **media type deserializers** and **format unmarshallers**
- [Security](security.md) data providers (API keys, Cookie, Basic, and Bearer HTTP authentications)

## Installation

=== "Pip + PyPI (recommended)"

    ``` console
    pip install openapi-core
    ```

=== "Pip + the source"

    ``` console
    pip install -e git+https://github.com/python-openapi/openapi-core.git#egg=openapi_core
    ```

## First steps

First, create your OpenAPI object.

```python
from openapi_core import OpenAPI

openapi = OpenAPI.from_file_path('openapi.json')
```

Now you can use it to validate and unmarshal your requests and/or responses.

```python
# raises an error if the request is invalid
result = openapi.unmarshal_request(request)
```

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

The request object should implement the OpenAPI Request protocol. Check [Integrations](integrations/index.md) to find officially supported implementations.

For more details, read about the [Unmarshalling](unmarshalling.md) process.

If you just want to validate your request/response data without unmarshalling, read about [Validation](validation.md) instead.

## Related projects

- [openapi-spec-validator](https://github.com/python-openapi/openapi-spec-validator)
  : A Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger), OpenAPI 3.0, and OpenAPI 3.1 specifications. The validator aims to check for full compliance with the Specification.
- [openapi-schema-validator](https://github.com/python-openapi/openapi-schema-validator)
  : A Python library that validates schemas against the OpenAPI Schema Specification v3.0 and OpenAPI Schema Specification v3.1.

## License

The project is under the terms of the BSD 3-Clause License.
