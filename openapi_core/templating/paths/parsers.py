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
        extra_types = {
            self.parse_path_parameter.name: self.parse_path_parameter
        }
        super().__init__(pattern, extra_types)
        self._expression: str = (
            pre_expression + self._expression + post_expression
        )

    def _handle_field(self, field: str) -> Any:
        # handle as path parameter field
        field = field[1:-1]
        path_parameter_field = "{%s:PathParameter}" % field
        return super()._handle_field(path_parameter_field)
