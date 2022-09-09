from typing import Optional

from openapi_core.validation.request.datatypes import Parameters


class ResultMock:
    def __init__(
        self,
        body: Optional[str] = None,
        parameters: Optional[Parameters] = None,
        data: Optional[str] = None,
        error_to_raise: Optional[Exception] = None,
    ):
        self.body = body
        self.parameters = parameters
        self.data = data
        self.error_to_raise = error_to_raise

    def raise_for_errors(self) -> None:
        if self.error_to_raise is not None:
            raise self.error_to_raise
