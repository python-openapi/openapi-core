Request unmarshaller
====================

By default, request unmarshaller is selected based on detected specification version.

In order to explicitly validate and unmarshal a:

* OpenAPI 3.0 spec, import ``V30RequestUnmarshaller``
* OpenAPI 3.1 spec, import ``V31RequestUnmarshaller`` or ``V31WebhookRequestUnmarshaller``

.. code-block:: python
  :emphasize-lines: 1,4

    from openapi_core import V31RequestUnmarshaller

    config = Config(
       request_unmarshaller_cls=V31RequestUnmarshaller,
    )
    openapi = OpenAPI.from_file_path('openapi.json', config=config)
    result = openapi.unmarshal_request(request)

You can also explicitly import ``V3RequestUnmarshaller`` which is a shortcut to the latest OpenAPI v3 version.
