from typing import Awaitable
from typing import Callable
from typing import Iterable

from openapi_core.typing import ResponseType
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult

ErrorsHandlerCallable = Callable[[Iterable[Exception]], ResponseType]
ValidRequestHandlerCallable = Callable[[RequestUnmarshalResult], ResponseType]
AsyncValidRequestHandlerCallable = Callable[
    [RequestUnmarshalResult], Awaitable[ResponseType]
]
