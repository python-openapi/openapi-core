"""OpenAPI core infos models module"""


class Info(object):

    def __init__(
            self, title, version, description=None, terms_of_service=None,
            contact=None, license=None, extensions=None,
    ):
        self.title = title
        self.version = version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = contact
        self.license = license

        self.extensions = extensions and dict(extensions) or {}
