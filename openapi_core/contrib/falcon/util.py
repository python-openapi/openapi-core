import warnings
from typing import Any
from typing import Generator
from typing import Mapping
from typing import Optional
from typing import Tuple

from falcon.request import Request


def serialize_body(
    request: Request,
    media: Any,
    content_type: str,
) -> Optional[bytes]:
    """Serialize request body using media handlers."""
    handler, _, _ = request.options.media_handlers._resolve(
        content_type,
        request.options.default_media_type,
    )
    try:
        body = handler.serialize(media, content_type=content_type)
    # multipart form serialization is not supported
    except NotImplementedError:
        warnings.warn(f"body serialization for {content_type} not supported")
        return None
    assert isinstance(body, bytes)
    return body


def unpack_params(
    params: Mapping[str, Any],
) -> Generator[Tuple[str, Any], None, None]:
    for k, v in params.items():
        if isinstance(v, list):
            for v2 in v:
                yield (k, v2)
        else:
            yield (k, v)
