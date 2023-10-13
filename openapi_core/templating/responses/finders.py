from jsonschema_path import SchemaPath

from openapi_core.templating.responses.exceptions import ResponseNotFound


class ResponseFinder:
    def __init__(self, responses: SchemaPath):
        self.responses = responses

    def find(self, http_status: str = "default") -> SchemaPath:
        if http_status in self.responses:
            return self.responses / http_status

        # try range
        http_status_range = f"{http_status[0]}XX"
        if http_status_range in self.responses:
            return self.responses / http_status_range

        if "default" not in self.responses:
            raise ResponseNotFound(http_status, list(self.responses.keys()))

        return self.responses / "default"
