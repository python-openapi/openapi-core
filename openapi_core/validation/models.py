"""OpenAPI core validation models module"""


class BaseValidationResult(object):

    def __init__(self, errors):
        self.errors = errors

    def raise_for_errors(self):
        for error in self.errors:
            raise error
