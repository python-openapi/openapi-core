from typing import Optional

from fastapi import Response

from openapi_core.contrib.starlette.responses import StarletteOpenAPIResponse


class FastAPIOpenAPIResponse(StarletteOpenAPIResponse):
    def __init__(self, response: Response, data: Optional[bytes] = None):
        super().__init__(response, data=data)
