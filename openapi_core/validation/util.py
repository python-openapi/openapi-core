"""OpenAPI core validation util module"""
from yarl import URL


def get_operation_pattern(server_url, request_url_pattern):
    """Return an updated request URL pattern with the server URL removed."""
    if server_url[-1] == "/":
        # operations have to start with a slash, so do not remove it
        server_url = server_url[:-1]
    if URL(server_url).is_absolute():
        return request_url_pattern.replace(server_url, "", 1)
    return URL(request_url_pattern).path_qs.replace(server_url, "", 1)
