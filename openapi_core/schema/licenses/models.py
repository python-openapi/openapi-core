"""OpenAPI core licenses models module"""


class License(object):

    def __init__(self, name, url=None):
        self.name = name
        self.url = url
