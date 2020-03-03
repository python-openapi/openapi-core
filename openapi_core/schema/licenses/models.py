"""OpenAPI core licenses models module"""


class License(object):

    def __init__(self, name, url=None, extensions=None):
        self.name = name
        self.url = url

        self.extensions = extensions and dict(extensions) or {}
