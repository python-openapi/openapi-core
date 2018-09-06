# -*- coding: utf-8 -*-
"""OpenAPI core specs models module"""
import logging

from openapi_core.compat import partialmethod
from openapi_core.schema.operations.exceptions import InvalidOperation
from openapi_core.schema.servers.exceptions import InvalidServer


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

        raise InvalidServer(full_url_pattern)

    def get_server_url(self, index=0):
        return self.servers[index].default_url

    def get_operation(self, path_pattern, http_method):
        try:
            return self.paths[path_pattern].operations[http_method]
        except KeyError:
            raise InvalidOperation(path_pattern, http_method)

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
