"""OpenAPI core contrib falcon responses module"""
import json

from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters
from werkzeug.datastructures import ImmutableMultiDict


class FalconOpenAPIRequestFactory:
    @classmethod
    def create(cls, req, route_params):
        """
        Create OpenAPIRequest from falcon Request and route params.
        """
        method = req.method.lower()

        # Convert keys to lowercase as that's what the OpenAPIRequest expects.
        headers = {key.lower(): value for key, value in req.headers.items()}

        parameters = RequestParameters(
            path=route_params,
            query=ImmutableMultiDict(req.params.items()),
            header=headers,
            cookie=req.cookies,
        )
        return OpenAPIRequest(
            host_url=req.host,
            path=req.path,
            path_pattern=req.uri_template,
            method=method,
            parameters=parameters,
            # Support falcon-jsonify.
            body=json.dumps(req.json)
            if getattr(req, "json", None)
            else req.bounded_stream.read(),
            mimetype=req.content_type.partition(";")[0] if req.content_type else "",
        )
