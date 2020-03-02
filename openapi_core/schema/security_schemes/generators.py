"""OpenAPI core security schemes generators module"""
import logging

from six import iteritems

from openapi_core.schema.security_schemes.models import SecurityScheme

log = logging.getLogger(__name__)


class SecuritySchemesGenerator(object):

    def __init__(self, dereferencer):
        self.dereferencer = dereferencer

    def generate(self, security_schemes_spec):
        security_schemes_deref = self.dereferencer.dereference(
            security_schemes_spec)

        for scheme_name, scheme_spec in iteritems(security_schemes_deref):
            scheme_deref = self.dereferencer.dereference(scheme_spec)
            scheme_type = scheme_deref['type']
            description = scheme_deref.get('description')
            name = scheme_deref.get('name')
            apikey_in = scheme_deref.get('in')
            scheme = scheme_deref.get('scheme')
            bearer_format = scheme_deref.get('bearerFormat')
            flows = scheme_deref.get('flows')
            open_id_connect_url = scheme_deref.get('openIdConnectUrl')

            scheme = SecurityScheme(
                scheme_type, description=description, name=name,
                apikey_in=apikey_in, scheme=scheme,
                bearer_format=bearer_format, flows=flows,
                open_id_connect_url=open_id_connect_url,
            )
            yield scheme_name, scheme
