from typing import TypedDict


class FlaskOpenAPIError(TypedDict):
    name: str
    message: str
    status: int
