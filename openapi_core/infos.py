class Info(object):

    def __init__(self, title, version):
        self.title = title
        self.version = version


class InfoFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, info_spec):
        info_deref = self.dereferencer.dereference(info_spec)
        title = info_deref['title']
        version = info_deref['version']
        return Info(title, version)
