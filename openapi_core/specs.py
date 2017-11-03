# -*- coding: utf-8 -*-
"""OpenAPI core specs module"""
import logging
from functools import partialmethod, lru_cache

from openapi_spec_validator import openapi_v3_spec_validator

from openapi_core.components import ComponentsFactory
from openapi_core.exceptions import InvalidOperation, InvalidServer
from openapi_core.infos import InfoFactory
from openapi_core.paths import PathsGenerator
from openapi_core.schemas import SchemaRegistry
from openapi_core.servers import ServersGenerator


log = logging.getLogger(__name__)


class Spec(object):
    """Represents an OpenAPI Specification for a service."""

    def __init__(self, info, paths, servers=None, components=None):
        self.info = info
        self.paths = paths and dict(paths)
        self.servers = servers or []
        self.components = components

    def __getitem__(self, path_name):
        return self.paths[path_name]

    @property
    def default_url(self):
        return self.servers[0].default_url

    def get_server(self, full_url_pattern):
        for spec_server in self.servers:
            if spec_server.default_url in full_url_pattern:
                return spec_server

        raise InvalidServer(
            "Invalid request server {0}".format(full_url_pattern))

    def get_server_url(self, index=0):
        return self.servers[index].default_url

    def get_operation(self, path_pattern, http_method):
        try:
            return self.paths[path_pattern].operations[http_method]
        except KeyError:
            raise InvalidOperation(
                "Unknown operation path {0} with method {1}".format(
                    path_pattern, http_method))

    def get_schema(self, name):
        return self.components.schemas[name]

    # operations shortcuts

    get = partialmethod(get_operation, http_method='get')
    put = partialmethod(get_operation, http_method='put')
    post = partialmethod(get_operation, http_method='post')
    delete = partialmethod(get_operation, http_method='delete')
    options = partialmethod(get_operation, http_method='options')
    head = partialmethod(get_operation, http_method='head')
    patch = partialmethod(get_operation, http_method='patch')


class SpecFactory(object):

    def __init__(self, dereferencer, config=None):
        self.dereferencer = dereferencer
        self.config = config or {}

    def create(self, spec_dict, spec_url=''):
        if self.config.get('validate_spec', True):
            openapi_v3_spec_validator.validate(spec_dict, spec_url=spec_url)

        spec_dict_deref = self.dereferencer.dereference(spec_dict)

        info_spec = spec_dict_deref.get('info', [])
        servers_spec = spec_dict_deref.get('servers', [])
        paths = spec_dict_deref.get('paths', [])
        components_spec = spec_dict_deref.get('components', [])

        info = self.info_factory.create(info_spec)
        servers = self.servers_generator.generate(servers_spec)
        paths = self.paths_generator.generate(paths)
        components = self.components_factory.create(components_spec)
        spec = Spec(
            info, list(paths), servers=list(servers), components=components)
        return spec

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
