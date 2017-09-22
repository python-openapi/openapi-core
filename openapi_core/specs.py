# -*- coding: utf-8 -*-
"""OpenAPI core specs module"""
import logging
from functools import partialmethod

from openapi_spec_validator import openapi_v3_spec_validator

from openapi_core.components import ComponentsFactory
from openapi_core.infos import InfoFactory
from openapi_core.paths import PathsGenerator


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

    def get_server_url(self, index=0):
        return self.servers[index]['url']

    def get_operation(self, path_pattern, http_method):
        return self.paths[path_pattern].operations[http_method]

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
        servers = spec_dict_deref.get('servers', [])
        paths = spec_dict_deref.get('paths', [])
        components_spec = spec_dict_deref.get('components', [])

        info = self._create_info(info_spec)
        paths = self._generate_paths(paths)
        components = self._create_components(components_spec)
        spec = Spec(info, list(paths), servers=servers, components=components)
        return spec

    def _create_info(self, info_spec):
        return InfoFactory(self.dereferencer).create(info_spec)

    def _generate_paths(self, paths):
        return PathsGenerator(self.dereferencer).generate(paths)

    def _create_components(self, components_spec):
        return ComponentsFactory(self.dereferencer).create(components_spec)
