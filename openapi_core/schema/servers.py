from typing import Dict

from openapi_core.spec.paths import SpecPath


def is_absolute(url: str) -> bool:
    return url.startswith('//') or '://' in url


def get_server_default_variables(server: SpecPath) -> dict:
    if 'variables' not in server:
        return {}

    defaults = {}
    variables = server / 'variables'
    for name, variable in list(variables.items()):
        defaults[name] = variable['default']
    return defaults


def get_server_url(server: SpecPath, **variables: Dict[str, str]) -> str:
    if not variables:
        variables = get_server_default_variables(server)
    server_url: str = server['url']
    return server_url.format(**variables)
