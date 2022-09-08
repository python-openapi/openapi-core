from typing import Tuple

from openapi_core.spec.paths import Spec
from openapi_core.templating.paths.datatypes import Path


def template_path_len(template_path: Path) -> int:
    return len(template_path[1].variables)
