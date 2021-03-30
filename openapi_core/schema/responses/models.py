"""OpenAPI core responses models module"""


class Response(object):

    def __init__(
            self, http_status, description, headers=None, content=None,
            links=None, extensions=None):
        self.http_status = http_status
        self.description = description
        self.headers = headers and dict(headers) or {}
        self.content = content
        self.links = links and dict(links) or {}

        self.extensions = extensions and dict(extensions) or {}
