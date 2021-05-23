from typing import NamedTuple

from openapi_core.spec.paths import SpecPath


class MediaTypeResult(NamedTuple):
    media_type: SpecPath
    mimetype: str
