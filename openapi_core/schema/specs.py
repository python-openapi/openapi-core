from jsonschema_path import SchemaPath

from openapi_core.schema.servers import get_server_url


def get_spec_url(spec: SchemaPath, index: int = 0) -> str:
    servers = spec / "servers"
    return get_server_url(servers / 0)
