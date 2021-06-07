from typing import Tuple

from openapi_core.spec.paths import SpecPath
from openapi_core.templating.datatypes import TemplateResult


def template_path_len(template_path: Tuple[SpecPath, TemplateResult]) -> int:
    return len(template_path[1].variables)
