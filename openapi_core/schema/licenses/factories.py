"""OpenAPI core licenses factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.licenses.models import License


class LicenseFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, license_spec):
        license_deref = self.dereferencer.dereference(license_spec)
        name = license_deref['name']
        url = license_deref.get('url')

        extensions = self.extensions_generator.generate(license_deref)

        return License(name, url=url, extensions=extensions)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
