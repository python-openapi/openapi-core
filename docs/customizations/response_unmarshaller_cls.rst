Response unmarshaller
=====================

In order to explicitly validate and unmarshal a:

* OpenAPI 3.0 spec, import ``V30ResponseUnmarshaller`` 
* OpenAPI 3.1 spec, import ``V31ResponseUnmarshaller`` or ``V31WebhookResponseUnmarshaller`` 

.. code-block:: python
  :emphasize-lines: 1,4

    from openapi_core import V31ResponseUnmarshaller

    config = Config(
       response_unmarshaller_cls=V31ResponseUnmarshaller,
    )
    openapi = OpenAPI.from_file_path('openapi.json', config=config)
    result = openapi.unmarshal_response(request, response)

You can also explicitly import ``V3ResponseUnmarshaller``  which is a shortcut to the latest OpenAPI v3 version.
