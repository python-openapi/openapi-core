from contextlib import contextmanager
from typing import Any
from typing import Hashable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Union

from openapi_spec_validator.validators import Dereferencer
from pathable.accessors import LookupAccessor


class SpecAccessor(LookupAccessor):
    def __init__(
        self, lookup: Mapping[Hashable, Any], dereferencer: Dereferencer
    ):
        super().__init__(lookup)
        self.dereferencer = dereferencer

    @contextmanager
    def open(
        self, parts: List[Hashable]
    ) -> Iterator[Union[Mapping[Hashable, Any], Any]]:
        content = self.lookup
        for part in parts:
            content = content[part]
            if "$ref" in content:
                content = self.dereferencer.dereference(content)
        try:
            yield content
        finally:
            pass
