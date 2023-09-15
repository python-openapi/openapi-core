from typing import Callable
from typing import Iterable
from typing import TypeVar

from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult

#: The type of request within an integration.
RequestType = TypeVar("RequestType")
#: The type of response within an integration.
ResponseType = TypeVar("ResponseType")

ErrorsHandlerCallable = Callable[[Iterable[Exception]], ResponseType]
ValidRequestHandlerCallable = Callable[[RequestUnmarshalResult], ResponseType]
