"""OpenAPI core contacts models module"""


class Contact(object):

    def __init__(self, name=None, url=None, email=None, extensions=None):
        self.name = name
        self.url = url
        self.email = email

        self.extensions = extensions and dict(extensions) or {}
