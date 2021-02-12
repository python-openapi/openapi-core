# -*- coding: utf-8 -*-
"""OpenAPI core specs factories module"""

from openapi_spec_validator.validators import Dereferencer

from openapi_core.compat import lru_cache
from openapi_core.schema.components.factories import ComponentsFactory
from openapi_core.schema.extensions.generators import ExtensionsGenerator
from openapi_core.schema.infos.factories import InfoFactory
from openapi_core.schema.paths.generators import PathsGenerator
from openapi_core.schema.schemas.registries import SchemaRegistry
from openapi_core.schema.security_requirements.generators import (
    SecurityRequirementsGenerator,
)
from openapi_core.schema.servers.generators import ServersGenerator
from openapi_core.schema.specs.models import Spec


class SpecFactory(object):

    def __init__(self, spec_resolver):
        self.spec_resolver = spec_resolver

    def create(self, spec_dict, spec_url=''):
        spec_dict_deref = self.dereferencer.dereference(spec_dict)

        info_spec = spec_dict_deref.get('info', {})
        servers_spec = spec_dict_deref.get('servers', [])
        paths = spec_dict_deref.get('paths', {})
        components_spec = spec_dict_deref.get('components', {})
        security_spec = spec_dict_deref.get('security', [])

        if not servers_spec:
            servers_spec = [
                {'url': '/'},
            ]

        extensions = self.extensions_generator.generate(spec_dict_deref)

        info = self.info_factory.create(info_spec)
        servers = self.servers_generator.generate(servers_spec)
        paths = self.paths_generator.generate(paths)
        components = self.components_factory.create(components_spec)

        security = self.security_requirements_generator.generate(
                security_spec)

        spec = Spec(
            info, list(paths), servers=list(servers), components=components,
            security=list(security), extensions=extensions,
            _resolver=self.spec_resolver,
        )
        return spec

    @property
    @lru_cache()
    def dereferencer(self):
        return Dereferencer(self.spec_resolver)

    @property
    @lru_cache()
    def schemas_registry(self):
        return SchemaRegistry(self.dereferencer)

    @property
    @lru_cache()
    def info_factory(self):
        return InfoFactory(self.dereferencer)

    @property
    @lru_cache()
    def servers_generator(self):
        return ServersGenerator(self.dereferencer)

    @property
    @lru_cache()
    def paths_generator(self):
        return PathsGenerator(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def components_factory(self):
        return ComponentsFactory(self.dereferencer, self.schemas_registry)

    @property
    @lru_cache()
    def security_requirements_generator(self):
        return SecurityRequirementsGenerator(self.dereferencer)

    @property
    @lru_cache()
    def extensions_generator(self):
        return ExtensionsGenerator(self.dereferencer)
