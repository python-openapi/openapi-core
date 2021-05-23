from typing import NamedTuple

from openapi_core.spec.paths import SpecPath
from openapi_core.templating.datatypes import TemplateResult


class PathResult(NamedTuple):
    path: SpecPath
    path_template: TemplateResult


class OperationResult(NamedTuple):
    path: SpecPath
    operation: SpecPath
    path_template: TemplateResult


class ServerResult(NamedTuple):
    path: SpecPath
    operation: SpecPath
    server: SpecPath
    path_template: TemplateResult
    server_template: TemplateResult
