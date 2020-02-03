"""OpenAPI core contacts factories module"""
from openapi_core.schema.contacts.models import Contact


class ContactFactory(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def create(self, contact_spec):
        contact_deref = self.dereferencer.dereference(contact_spec)
        name = contact_deref.get('name')
        url = contact_deref.get('url')
        email = contact_deref.get('email')
        return Contact(name=name, url=url, email=email)
