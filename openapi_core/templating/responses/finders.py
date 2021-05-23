from openapi_core.spec.paths import SpecPath
from openapi_core.templating.responses.exceptions import ResponseNotFound


class ResponseFinder:

    def __init__(self, responses: SpecPath):
        self.responses = responses

    def find(self, http_status: str = 'default') -> SpecPath:
        response: SpecPath
        if http_status in self.responses:
            response = self.responses / http_status
            return response

        # try range
        http_status_range = f'{http_status[0]}XX'
        if http_status_range in self.responses:
            response = self.responses / http_status_range
            return response

        if 'default' not in self.responses:
            raise ResponseNotFound(http_status, list(self.responses.keys()))

        response = self.responses / 'default'
        return response
