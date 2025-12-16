from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from parse import Parser


class PathParameter:
    name = "PathParameter"
    pattern = r"[^\/]*"

    def __call__(self, text: str) -> str:
        return text


class PathParser(Parser):  # type: ignore

    parse_path_parameter = PathParameter()

    def __init__(
        self, pattern: str, pre_expression: str = "", post_expression: str = ""
    ) -> None:
        self._orig_to_safe: dict[str, str] = {}
        self._safe_to_orig: dict[str, str] = {}
        self._safe_suffix_counters: dict[str, int] = {}
        extra_types = {
            self.parse_path_parameter.name: self.parse_path_parameter
        }
        sanitized_pattern = self._sanitize_pattern(pattern)
        super().__init__(sanitized_pattern, extra_types)
        self._expression: str = (
            pre_expression + self._expression + post_expression
        )

    def search(self, string: str) -> Any:
        result = super().search(string)
        if not result:
            return result
        return _RemappedResult(result, self._safe_to_orig)

    def parse(self, string: str, **kwargs: Any) -> Any:
        result = super().parse(string, **kwargs)
        if not result:
            return result
        return _RemappedResult(result, self._safe_to_orig)

    def _get_safe_field_name(self, original: str) -> str:
        existing = self._orig_to_safe.get(original)
        if existing is not None:
            return existing

        safe_parts = []
        for ch in original:
            if ch == "_" or ch.isalnum():
                safe_parts.append(ch)
            else:
                safe_parts.append(f"__{ord(ch):x}__")

        safe = "".join(safe_parts) or "p"
        # `parse` and Python `re` named groups are most reliable when the group name
        # starts with a letter.
        if not safe[0].isalpha():
            safe = f"p_{safe}"

        # Ensure uniqueness across fields within this parser
        if safe in self._safe_to_orig and self._safe_to_orig[safe] != original:
            base = safe
            suffix = self._safe_suffix_counters.get(base, 1)
            while True:
                candidate = f"{base}__{suffix}"
                if candidate not in self._safe_to_orig:
                    safe = candidate
                    self._safe_suffix_counters[base] = suffix + 1
                    break
                suffix += 1

        self._orig_to_safe[original] = safe
        self._safe_to_orig[safe] = original
        return safe

    def _sanitize_pattern(self, pattern: str) -> str:
        # Pre-sanitize field names inside `{...}` before `parse` processes them.
        # This ensures special characters (e.g. `~`) and digit-leading names are
        # treated as named fields instead of literals or positional groups.
        if "{" not in pattern:
            return pattern

        out: list[str] = []
        i = 0
        n = len(pattern)
        while i < n:
            ch = pattern[i]
            if ch != "{":
                out.append(ch)
                i += 1
                continue

            end = pattern.find("}", i + 1)
            if end == -1:
                out.append(ch)
                i += 1
                continue

            original = pattern[i + 1 : end]
            safe = self._get_safe_field_name(original)
            out.append("{")
            out.append(safe)
            out.append("}")
            i = end + 1

        return "".join(out)

    def _handle_field(self, field: str) -> Any:
        # handle as path parameter field
        safe_field = field[1:-1]
        path_parameter_field = "{%s:PathParameter}" % safe_field
        return super()._handle_field(path_parameter_field)


@dataclass(frozen=True)
class _RemappedResult:
    _result: Any
    _safe_to_orig: dict[str, str]

    @property
    def named(self) -> dict[str, Any]:
        named = getattr(self._result, "named", {})
        return {self._safe_to_orig.get(k, k): v for k, v in named.items()}

    def __bool__(self) -> bool:
        return bool(self._result)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._result, item)
