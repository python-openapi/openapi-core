.. openapi-core documentation master file, created by
   sphinx-quickstart on Tue Feb  2 17:41:34 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to openapi-core's documentation!
========================================

Openapi-core is a Python library that adds client-side and server-side support
for the `OpenAPI Specification v3 <https://github.com/OAI/OpenAPI-Specification>`__.

Key features
------------

* **Validation** of requests and responses
* Schema **casting** and **unmarshalling**
* Media type and parameters **deserialization**
* **Security** providers (API keys, Cookie, Basic and Bearer HTTP authentications)
* Custom **deserializers** and **formats**
* **Integration** with libraries and frameworks


Table of contents
-----------------

.. Navigation/TOC

.. toctree::
   :maxdepth: 2

   installation
   usage
   customizations
   integrations


Related projects
================

* `openapi-spec-validator <https://github.com/p1c2u/openapi-spec-validator>`__
   Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger) and OpenAPI 3.0.0 specification. The validator aims to check for full compliance with the Specification.
* `openapi-schema-validator <https://github.com/p1c2u/openapi-schema-validator>`__
   Python library that validates schema against the OpenAPI Schema Specification v3.0 which is an extended subset of the JSON Schema Specification Wright Draft 00.
