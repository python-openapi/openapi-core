Format unmarshallers
====================

Based on ``format`` keyword, openapi-core can also unmarshal values to specific formats.

Openapi-core comes with a set of built-in format unmarshallers, but it's also possible to add custom ones.

Here's an example with the ``usdate`` format that converts a value to date object:

.. code-block:: python
  :emphasize-lines: 11

    from datetime import datetime

    def unmarshal_usdate(value):
       return datetime.strptime(value, "%m/%d/%y").date

    extra_format_unmarshallers = {
       'usdate': unmarshal_usdate,
    }

    config = Config(
       extra_format_unmarshallers=extra_format_unmarshallers,
    )
    openapi = OpenAPI.from_file_path('openapi.json', config=config)

    result = openapi.unmarshal_response(request, response)
