"""OpenAPI core infos factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.contacts.factories import ContactFactory
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.infos.models import Info
from openapi_core.schema.licenses.factories import LicenseFactory


class InfoFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, info_spec):
        info_deref = self.dereferencer.dereference(info_spec)
        title = info_deref['title']
        version = info_deref['version']
        description = info_deref.get('description')
        terms_of_service = info_deref.get('termsOfService')

        extensions = self.extensions_generator.generate(info_deref)

        contact = None
        if 'contact' in info_deref:
            contact_spec = info_deref.get('contact')
            contact = self.contact_factory.create(contact_spec)

        license = None
        if 'license' in info_deref:
            license_spec = info_deref.get('license')
            license = self.license_factory.create(license_spec)

        return Info(
            title, version,
            description=description, terms_of_service=terms_of_service,
            contact=contact, license=license, extensions=extensions,
        )

    @property
    @lru_cache()
    def contact_factory(self):
        return ContactFactory(self.dereferencer)

    @property
    @lru_cache()
    def license_factory(self):
        return LicenseFactory(self.dereferencer)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
