from typing import Any
from typing import Dict

from jsonschema_path import SchemaPath


def is_absolute(url: str) -> bool:
    return url.startswith("//") or "://" in url


def get_server_default_variables(server: SchemaPath) -> Dict[str, Any]:
    if "variables" not in server:
        return {}

    defaults = {}
    variables = server / "variables"
    for name, variable in list(variables.str_items()):
        defaults[name] = (variable / "default").read_value()
    return defaults


def get_server_url(server: SchemaPath, **variables: Any) -> str:
    if not variables:
        variables = get_server_default_variables(server)
    url = (server / "url").read_value()
    assert isinstance(url, str)
    return url.format(**variables)
