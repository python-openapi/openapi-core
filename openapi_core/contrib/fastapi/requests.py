from fastapi import Request

from openapi_core.contrib.starlette.requests import StarletteOpenAPIRequest


class FastAPIOpenAPIRequest(StarletteOpenAPIRequest):
    def __init__(self, request: Request):
        super().__init__(request)
