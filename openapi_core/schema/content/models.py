"""OpenAPI core content models module"""
import fnmatch

from six import iteritems

from openapi_core.schema.content.exceptions import MimeTypeNotFound


class Content(dict):

    def __getitem__(self, mimetype):
        try:
            return super(Content, self).__getitem__(mimetype)
        except KeyError:
            pass

        for key, value in iteritems(self):
            if fnmatch.fnmatch(mimetype, key):
                return value

        raise MimeTypeNotFound(mimetype, self.keys())
