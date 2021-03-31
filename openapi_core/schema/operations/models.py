# -*- coding: utf-8 -*-
"""OpenAPI core operations models module"""


class Operation(object):
    """Represents an OpenAPI Operation."""

    def __init__(
            self, http_method, path_name, responses, parameters,
            summary=None, description=None, external_docs=None, security=None,
            request_body=None, deprecated=False, operation_id=None, tags=None,
            servers=None, extensions=None):
        self.http_method = http_method
        self.path_name = path_name
        self.responses = dict(responses)
        self.parameters = dict(parameters)
        self.summary = summary
        self.description = description
        self.external_docs = external_docs
        self.security = security and list(security)
        self.request_body = request_body
        self.deprecated = deprecated
        self.operation_id = operation_id
        self.tags = tags
        self.servers = servers

        self.extensions = extensions and dict(extensions) or {}

    def __getitem__(self, name):
        return self.parameters[name]
