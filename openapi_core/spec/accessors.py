from contextlib import contextmanager

from pathable.accessors import LookupAccessor


class SpecAccessor(LookupAccessor):
    def __init__(self, lookup, dereferencer):
        super().__init__(lookup)
        self.dereferencer = dereferencer

    @contextmanager
    def open(self, parts):
        content = self.lookup
        for part in parts:
            content = content[part]
            if "$ref" in content:
                content = self.dereferencer.dereference(content)
        try:
            yield content
        finally:
            pass
