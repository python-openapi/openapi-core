"""OpenAPI core validation util module"""
from six.moves.urllib.parse import urlparse


def is_absolute(url):
    return url.startswith('//') or '://' in url


def path_qs(url):
    pr = urlparse(url)
    result = pr.path
    if pr.query:
        result += '?' + pr.query
    return result


def get_operation_pattern(server_url, request_url_pattern):
    """Return an updated request URL pattern with the server URL removed."""
    if server_url[-1] == "/":
        # operations have to start with a slash, so do not remove it
        server_url = server_url[:-1]
    if is_absolute(server_url):
        return request_url_pattern.replace(server_url, "", 1)
    return path_qs(request_url_pattern).replace(server_url, "", 1)
