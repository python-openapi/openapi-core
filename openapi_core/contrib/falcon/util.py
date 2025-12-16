from typing import Any
from typing import Generator
from typing import Mapping
from typing import Tuple


def unpack_params(
    params: Mapping[str, Any],
) -> Generator[Tuple[str, Any], None, None]:
    for k, v in params.items():
        if isinstance(v, list):
            for v2 in v:
                yield (k, v2)
        else:
            yield (k, v)
