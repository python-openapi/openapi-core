"""OpenAPI core contrib falcon responses module"""
from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters


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
            path=route_params, query=req.params, header=headers, cookie=req.cookies
        )
        return OpenAPIRequest(
            host_url=req.host,
            path=req.path,
            path_pattern=req.uri_template,
            method=method,
            parameters=parameters,
            body=req.bounded_stream.read(),
            mimetype=req.content_type.partition(";")[0] if req.content_type else "",
        )
