# Allow writing union types as X | Y in Python 3.9
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PathMatchResult:
    """Result of path parsing."""

    named: dict[str, str]


class PathParser:
    """Parses path patterns with parameters into regex and matches against URLs."""

    _PARAM_PATTERN = r"[^/]*"

    def __init__(
        self, pattern: str, pre_expression: str = "", post_expression: str = ""
    ) -> None:
        self.pattern = pattern
        self._group_to_name: dict[str, str] = {}

        regex_body = self._compile_template_to_regex(pattern)
        self._expression = f"{pre_expression}{regex_body}{post_expression}"
        self._compiled = re.compile(self._expression)

    def search(self, text: str) -> PathMatchResult | None:
        """Searches for a match in the given text."""
        match = self._compiled.search(text)
        return self._to_result(match)

    def parse(self, text: str) -> PathMatchResult | None:
        """Parses the entire text for a match."""
        match = self._compiled.fullmatch(text)
        return self._to_result(match)

    def _compile_template_to_regex(self, template: str) -> str:
        parts: list[str] = []
        i = 0
        group_index = 0
        while i < len(template):
            start = template.find("{", i)
            if start == -1:
                parts.append(re.escape(template[i:]))
                break
            end = template.find("}", start + 1)
            if end == -1:
                raise ValueError(f"Unmatched '{{' in template: {template!r}")

            parts.append(re.escape(template[i:start]))
            param_name = template[start + 1 : end]
            group_name = f"g{group_index}"
            group_index += 1
            self._group_to_name[group_name] = param_name
            parts.append(f"(?P<{group_name}>{self._PARAM_PATTERN})")
            i = end + 1

        return "".join(parts)

    def _to_result(
        self, match: re.Match[str] | None
    ) -> PathMatchResult | None:
        if match is None:
            return None
        return PathMatchResult(
            named={
                param_name: match.group(group_name)
                for group_name, param_name in self._group_to_name.items()
            },
        )
