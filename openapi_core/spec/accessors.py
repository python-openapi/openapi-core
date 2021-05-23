from contextlib import contextmanager
from typing import Iterator, List, Union

from dictpath.accessors import DictOrListAccessor
from openapi_spec_validator.validators import Dereferencer


class SpecAccessor(DictOrListAccessor):

    def __init__(
        self,
        dict_or_list: Union[dict, list],
        dereferencer: Dereferencer,
    ):
        super().__init__(dict_or_list)
        self.dereferencer = dereferencer

    @contextmanager
    def open(self, parts: List[str]) -> Iterator[str]:
        content = self.dict_or_list
        for part in parts:
            content = content[part]
            if '$ref' in content:
                content = self.dereferencer.dereference(
                    content)
        try:
            yield content
        finally:
            pass
