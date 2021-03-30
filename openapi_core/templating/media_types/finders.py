"""OpenAPI core templating media types finders module"""
import fnmatch

from six import iteritems

from openapi_core.templating.media_types.exceptions import MediaTypeNotFound


class MediaTypeFinder(object):

    def __init__(self, content):
        self.content = content

    def find(self, request):
        try:
            return self.content[request.mimetype]
        except KeyError:
            pass

        for key, value in iteritems(self.content):
            if fnmatch.fnmatch(request.mimetype, key):
                return value

        raise MediaTypeNotFound(request.mimetype, list(self.content.keys()))
