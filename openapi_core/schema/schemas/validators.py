class TypeValidator(object):

    def __init__(self, *types, **options):
        self.types = types
        self.exclude = options.get('exclude')

    def __call__(self, value):
        if self.exclude is not None and isinstance(value, self.exclude):
            return False

        if not isinstance(value, self.types):
            return False

        return True


class AttributeValidator(object):

    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, value):
        if not hasattr(value, self.attribute):
            return False

        return True
