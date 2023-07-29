Security
========

Openapi-core provides you easy access to security data for authentication and authorization process.

Supported security schemas:

* http – for Basic and Bearer HTTP authentications schemes
* apiKey – for API keys and cookie authentication

Here's an example with scheme ``BasicAuth`` and ``ApiKeyAuth`` security schemes:

.. code-block:: yaml

    security:
     - BasicAuth: []
     - ApiKeyAuth: []
    components:
     securitySchemes:
       BasicAuth:
         type: http
         scheme: basic
       ApiKeyAuth:
         type: apiKey
         in: header
         name: X-API-Key

Security schemes data are accessible from `security` attribute of `RequestUnmarshalResult` object.

.. code-block:: python

    # get basic auth decoded credentials
    result.security['BasicAuth']

    # get api key
    result.security['ApiKeyAuth']
