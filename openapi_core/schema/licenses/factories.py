"""OpenAPI core licenses factories module"""
from openapi_core.schema.licenses.models import License


class LicenseFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, license_spec):
        license_deref = self.dereferencer.dereference(license_spec)
        name = license_deref['name']
        url = license_deref.get('url')
        return License(name, url=url)
