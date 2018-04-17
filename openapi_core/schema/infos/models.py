"""OpenAPI core infos models module"""


class Info(object):

    def __init__(self, title, version):
        self.title = title
        self.version = version
