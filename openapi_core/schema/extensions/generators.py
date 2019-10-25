"""OpenAPI core extensions generators module"""
from six import iteritems

from openapi_core.schema.extensions.models import Extension


class ExtensionsGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, item_spec):
        for field_name, value in iteritems(item_spec):
            if not field_name.startswith('x-'):
                continue
            yield field_name, Extension(field_name, value)
