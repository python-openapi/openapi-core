from typing import Any
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.protocols import Response
from openapi_core.unmarshalling.response.datatypes import (
    ResponseUnmarshalResult,
)
from openapi_core.unmarshalling.response.protocols import ResponseUnmarshaller
from openapi_core.unmarshalling.response.types import ResponseUnmarshallerType


class ResponseUnmarshallingProcessor:
    def __init__(
        self,
        spec: SchemaPath,
        response_unmarshaller_cls: ResponseUnmarshallerType,
        **unmarshaller_kwargs: Any
    ) -> None:
        self.spec = spec
        self.response_unmarshaller_cls = response_unmarshaller_cls
        self.unmarshaller_kwargs = unmarshaller_kwargs

        self._response_unmarshaller_cached: Optional[ResponseUnmarshaller] = (
            None
        )

    @property
    def response_unmarshaller(self) -> ResponseUnmarshaller:
        if self._response_unmarshaller_cached is None:
            self._response_unmarshaller_cached = (
                self.response_unmarshaller_cls(
                    self.spec, **self.unmarshaller_kwargs
                )
            )
        return self._response_unmarshaller_cached

    def process(
        self, request: Request, response: Response
    ) -> ResponseUnmarshalResult:
        return self.response_unmarshaller.unmarshal(request, response)
