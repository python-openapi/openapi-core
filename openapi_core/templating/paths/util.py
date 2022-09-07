from typing import Tuple

from openapi_core.spec.paths import Spec
from openapi_core.templating.datatypes import TemplateResult


def template_path_len(template_path: Tuple[Spec, TemplateResult]) -> int:
    return len(template_path[1].variables)
