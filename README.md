# openapi-core

<a href="https://pypi.python.org/pypi/openapi-core" target="_blank">
    <img src="https://img.shields.io/pypi/v/openapi-core.svg" alt="Package version">
</a>
<a href="https://travis-ci.org/python-openapi/openapi-core" target="_blank">
    <img src="https://travis-ci.org/python-openapi/openapi-core.svg?branch=master" alt="Continuous Integration">
</a>
<a href="https://codecov.io/github/python-openapi/openapi-core?branch=master" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/python-openapi/openapi-core/master.svg?style=flat" alt="Tests coverage">
</a>
<a href="https://pypi.python.org/pypi/openapi-core" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/openapi-core.svg" alt="Python versions">
</a>
<a href="https://pypi.python.org/pypi/openapi-core" target="_blank">
    <img src="https://img.shields.io/pypi/format/openapi-core.svg" alt="Package format">
</a>
<a href="https://pypi.python.org/pypi/openapi-core" target="_blank">
    <img src="https://img.shields.io/pypi/status/openapi-core.svg" alt="Development status">
</a>

## About

Openapi-core is a Python library that provides client-side and server-side support
for the [OpenAPI v3.0](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md)
and [OpenAPI v3.1](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md)
and [OpenAPI v3.2](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.2.0.md) specifications.


## Key features

- **Validation** and **unmarshalling** of request and response data (including webhooks)
- **Integration** with popular libraries (Requests, Werkzeug) and frameworks (Django, Falcon, Flask, Starlette)
- Customization with media type **deserializers** and format **unmarshallers**
- **Security** data providers (API keys, Cookie, Basic, and Bearer HTTP authentications)


## Documentation

Check documentation to see more details about the features. All documentation is in the "docs" directory and online at [openapi-core.readthedocs.io](https://openapi-core.readthedocs.io)

## Integrations compatibility matrix

Supported [Integrations](https://openapi-core.readthedocs.io/en/latest/integrations/) and it's versions:

| Integration | Version(s) | Level |
| --- | --- | --- |
| [AIOHTTP](https://openapi-core.readthedocs.io/en/latest/integrations/aiohttp/) | versions 3.8+ and 3.11+ tracks | Low-level request and response classes |
| [Django](https://openapi-core.readthedocs.io/en/latest/integrations/django/) | versions 4, 5, and 6 | Middleware, decorator and low level |
| [Falcon](https://openapi-core.readthedocs.io/en/latest/integrations/falcon/) | version 4 | Middleware and low-level classes |
| [FastAPI](https://openapi-core.readthedocs.io/en/latest/integrations/fastapi/) | versions 0.11x and 0.12x | Middleware (low-level via Starlette integration) |
| [Flask](https://openapi-core.readthedocs.io/en/latest/integrations/flask/) | versions 2 and 3 | View decorator, class-based view, and low-level classes |
| [Requests](https://openapi-core.readthedocs.io/en/latest/integrations/requests/) | default dependency set | Low-level request, webhook request, and response classes |
| [Starlette](https://openapi-core.readthedocs.io/en/latest/integrations/starlette/) | versions 0.4x and 0.5x | Middleware and low-level classes |
| [Werkzeug](https://openapi-core.readthedocs.io/en/latest/integrations/werkzeug/) | default dependency set | Low-level request and response classes |

## Installation

Recommended way (via pip):

``` console
pip install openapi-core
```

Alternatively you can download the code and install from the repository:

``` console
pip install -e git+https://github.com/python-openapi/openapi-core.git#egg=openapi_core
```


## First steps

First, create your OpenAPI object.

``` python
from openapi_core import OpenAPI

openapi = OpenAPI.from_file_path('openapi.json')
```

Now you can use it to validate and unmarshal against requests and/or responses. 

``` python
# raises an error if the request is invalid
result = openapi.unmarshal_request(request)
```

Retrieve validated and unmarshalled request data.

``` python
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

The request object should implement the OpenAPI Request protocol. Check [Integrations](https://openapi-core.readthedocs.io/en/latest/integrations/) to find officially supported implementations.

For more details read about the [Unmarshalling](https://openapi-core.readthedocs.io/en/latest/unmarshalling/) process.

If you just want to validate your request/response data without unmarshalling, read about [Validation](https://openapi-core.readthedocs.io/en/latest/validation/) instead.


## Related projects

- [openapi-spec-validator](https://github.com/python-openapi/openapi-spec-validator)
  : A Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger), OpenAPI 3.0, OpenAPI 3.1, and OpenAPI 3.2 specification. The validator aims to check for full compliance with the Specification.
- [openapi-schema-validator](https://github.com/python-openapi/openapi-schema-validator)
  : A Python library that validates schema against the OpenAPI Schema Specification v3.0, v3.1, and v3.2.
- [bottle-openapi-3](https://github.com/cope-systems/bottle-openapi-3)
  : OpenAPI 3.0 Support for the Bottle Web Framework
- [pyramid_openapi3](https://github.com/niteoweb/pyramid_openapi3)
  : Pyramid addon for OpenAPI3 validation of requests and responses.
- [tornado-openapi3](https://github.com/correl/tornado-openapi3)
  : Tornado OpenAPI 3 request and response validation library.

## License

The project is under the terms of the BSD 3-Clause License.
