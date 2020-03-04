"""OpenAPI core contacts factories module"""
from openapi_core.compat import lru_cache
from openapi_core.schema.contacts.models import Contact
from openapi_core.schema.extensions.generators import ExtensionsGenerator


class ContactFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, contact_spec):
        contact_deref = self.dereferencer.dereference(contact_spec)
        name = contact_deref.get('name')
        url = contact_deref.get('url')
        email = contact_deref.get('email')

        extensions = self.extensions_generator.generate(contact_deref)

        return Contact(name=name, url=url, email=email, extensions=extensions)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
