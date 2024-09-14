# Format validators

OpenAPI defines a `format` keyword that hints at how a value should be interpreted, e.g. a `string` with the type `date` should conform to the RFC 3339 date format.

OpenAPI comes with a set of built-in format validators, but it's also possible to add custom ones.

Here's how you could add support for a `usdate` format that handles dates of the form MM/DD/YYYY:

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
