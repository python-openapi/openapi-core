from typing import Any
from typing import Optional

from jsonschema_path import SchemaPath

from openapi_core.protocols import Request
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult
from openapi_core.unmarshalling.request.protocols import RequestUnmarshaller
from openapi_core.unmarshalling.request.types import RequestUnmarshallerType


class RequestUnmarshallingProcessor:
    def __init__(
        self,
        spec: SchemaPath,
        request_unmarshaller_cls: RequestUnmarshallerType,
        **unmarshaller_kwargs: Any
    ) -> None:
        self.spec = spec
        self.request_unmarshaller_cls = request_unmarshaller_cls
        self.unmarshaller_kwargs = unmarshaller_kwargs

        self._request_unmarshaller_cached: Optional[RequestUnmarshaller] = None

    @property
    def request_unmarshaller(self) -> RequestUnmarshaller:
        if self._request_unmarshaller_cached is None:
            self._request_unmarshaller_cached = self.request_unmarshaller_cls(
                self.spec, **self.unmarshaller_kwargs
            )
        return self._request_unmarshaller_cached

    def process(self, request: Request) -> RequestUnmarshalResult:
        return self.request_unmarshaller.unmarshal(request)
