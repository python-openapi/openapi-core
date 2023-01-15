Customizations
==============

Spec validation
---------------

By default, the provided specification is validated on ``Spec`` object creation time.

If you know you have a valid specification already, disabling the validator can improve the performance.

.. code-block:: python

   from openapi_core import Spec

   spec = Spec.from_dict(spec_dict, validator=None)

Deserializers
-------------

Pass custom defined media type deserializers dictionary with supported mimetypes as a key to `MediaTypeDeserializersFactory` and then pass it to `RequestValidator` or `ResponseValidator` constructor:

.. code-block:: python

   from openapi_core.deserializing.media_types.factories import MediaTypeDeserializersFactory

   def protobuf_deserializer(message):
       feature = route_guide_pb2.Feature()
       feature.ParseFromString(message)
       return feature

   custom_media_type_deserializers = {
       'application/protobuf': protobuf_deserializer,
   }
   media_type_deserializers_factory = MediaTypeDeserializersFactory(
       custom_deserializers=custom_media_type_deserializers,
   )

   result = validate_response(
       request, response,
       spec=spec,
       cls=V30ResponseValidator,
       media_type_deserializers_factory=media_type_deserializers_factory,
   )

Formats
-------

OpenAPI defines a ``format`` keyword that hints at how a value should be interpreted, e.g. a ``string`` with the type ``date`` should conform to the RFC 3339 date format.

Openapi-core comes with a set of built-in formatters, but it's also possible to add custom formatters in `SchemaUnmarshallersFactory` and pass it to `RequestValidator` or `ResponseValidator`.

Here's how you could add support for a ``usdate`` format that handles dates of the form MM/DD/YYYY:

.. code-block:: python

   from openapi_core.unmarshalling.schemas.factories import SchemaUnmarshallersFactory
   from openapi_schema_validator import OAS30Validator
   from datetime import datetime
   import re

   class USDateFormatter:
       def validate(self, value) -> bool:
           return bool(re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", value))

       def format(self, value):
           return datetime.strptime(value, "%m/%d/%y").date


   custom_formatters = {
       'usdate': USDateFormatter(),
   }
   schema_unmarshallers_factory = SchemaUnmarshallersFactory(
       OAS30Validator,
       custom_formatters=custom_formatters,
       context=UnmarshalContext.RESPONSE,
   )

   result = validate_response(
       request, response,
       spec=spec,
       cls=ResponseValidator,
       schema_unmarshallers_factory=schema_unmarshallers_factory,
   )

