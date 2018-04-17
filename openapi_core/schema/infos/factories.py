"""OpenAPI core infos factories module"""
from openapi_core.schema.infos.models import Info


class InfoFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, info_spec):
        info_deref = self.dereferencer.dereference(info_spec)
        title = info_deref['title']
        version = info_deref['version']
        return Info(title, version)
