from openapi_core.schema.servers import get_server_url
from openapi_core.spec import Spec


def get_spec_url(spec: Spec, index: int = 0) -> str:
    servers = spec / "servers"
    return get_server_url(servers / 0)
