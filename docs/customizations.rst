Customizations
==============

Spec validation
---------------

By default, spec dict is validated on spec creation time. Disabling the validation can improve the performance.

.. code-block:: python

   from openapi_core import create_spec

   spec = create_spec(spec_dict, validate_spec=False)

Deserializers
-------------

Pass custom defined media type deserializers dictionary with supported mimetypes as a key to `RequestValidator` or `ResponseValidator` constructor:

.. code-block:: python

   def protobuf_deserializer(message):
       feature = route_guide_pb2.Feature()
       feature.ParseFromString(message)
       return feature

   custom_media_type_deserializers = {
       'application/protobuf': protobuf_deserializer,
   }

   validator = ResponseValidator(
       spec, custom_media_type_deserializers=custom_media_type_deserializers)

   result = validator.validate(request, response)

Formats
-------

OpenAPI defines a ``format`` keyword that hints at how a value should be interpreted, e.g. a ``string`` with the type ``date`` should conform to the RFC 3339 date format.

Openapi-core comes with a set of built-in formatters, but it's also possible to add support for custom formatters for `RequestValidator` and `ResponseValidator`.

Here's how you could add support for a ``usdate`` format that handles dates of the form MM/DD/YYYY:

.. code-block:: python

    from datetime import datetime
    import re

    class USDateFormatter:
        def validate(self, value) -> bool:
            return bool(re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", value))

        def unmarshal(self, value):
            return datetime.strptime(value, "%m/%d/%y").date


   custom_formatters = {
       'usdate': USDateFormatter(),
   }

   validator = ResponseValidator(spec, custom_formatters=custom_formatters)

   result = validator.validate(request, response)

