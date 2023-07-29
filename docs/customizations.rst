Customizations
==============

Specification validation
------------------------

By default, the provided specification is validated on ``Spec`` object creation time.

If you know you have a valid specification already, disabling the validator can improve the performance.

.. code-block:: python
  :emphasize-lines: 5

    from openapi_core import Spec

    spec = Spec.from_dict(
       spec_dict,
       validator=None,
    )

Media type deserializers
------------------------

OpenAPI comes with a set of built-in media type deserializers such as: ``application/json``, ``application/xml``, ``application/x-www-form-urlencoded`` or ``multipart/form-data``.

You can also define your own ones. Pass custom defined media type deserializers dictionary with supported mimetypes as a key to `unmarshal_response` function:

.. code-block:: python
  :emphasize-lines: 13

    def protobuf_deserializer(message):
       feature = route_guide_pb2.Feature()
       feature.ParseFromString(message)
       return feature

    extra_media_type_deserializers = {
       'application/protobuf': protobuf_deserializer,
    }

    result = unmarshal_response(
       request, response,
       spec=spec,
       extra_media_type_deserializers=extra_media_type_deserializers,
    )

Format validators
-----------------

OpenAPI defines a ``format`` keyword that hints at how a value should be interpreted, e.g. a ``string`` with the type ``date`` should conform to the RFC 3339 date format.

OpenAPI comes with a set of built-in format validators, but it's also possible to add custom ones.

Here's how you could add support for a ``usdate`` format that handles dates of the form MM/DD/YYYY:

.. code-block:: python
  :emphasize-lines: 13

    import re

    def validate_usdate(value):
       return bool(re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", value))

    extra_format_validators = {
       'usdate': validate_usdate,
    }

    validate_response(
       request, response,
       spec=spec,
       extra_format_validators=extra_format_validators,
    )

Format unmarshallers
--------------------

Based on ``format`` keyword, openapi-core can also unmarshal values to specific formats.

Openapi-core comes with a set of built-in format unmarshallers, but it's also possible to add custom ones.

Here's an example with the ``usdate`` format that converts a value to date object:

.. code-block:: python
  :emphasize-lines: 13

    from datetime import datetime

    def unmarshal_usdate(value):
       return datetime.strptime(value, "%m/%d/%y").date

    extra_format_unmarshallers = {
       'usdate': unmarshal_usdate,
    }

    result = unmarshal_response(
       request, response,
       spec=spec,
       extra_format_unmarshallers=extra_format_unmarshallers,
    )
