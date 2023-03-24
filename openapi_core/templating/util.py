from typing import Any
from typing import Optional

from parse import Match
from parse import Parser


class ExtendedParser(Parser):  # type: ignore
    def _handle_field(self, field: str) -> Any:
        # handle as path parameter field
        field = field[1:-1]
        path_parameter_field = "{%s:PathParameter}" % field
        return super()._handle_field(path_parameter_field)


class PathParameter:
    name = "PathParameter"
    pattern = r"[^\/]*"

    def __call__(self, text: str) -> str:
        return text


parse_path_parameter = PathParameter()


def search(path_pattern: str, full_url_pattern: str) -> Optional[Match]:
    extra_types = {parse_path_parameter.name: parse_path_parameter}
    p = ExtendedParser(path_pattern, extra_types)
    p._expression = p._expression + "$"
    return p.search(full_url_pattern)


def parse(server_url: str, server_url_pattern: str) -> Match:
    extra_types = {parse_path_parameter.name: parse_path_parameter}
    p = ExtendedParser(server_url, extra_types)
    p._expression = "^" + p._expression
    return p.parse(server_url_pattern)
