"""OpenAPI core contacts models module"""


class Contact(object):

    def __init__(self, name=None, url=None, email=None):
        self.name = name
        self.url = url
        self.email = email
