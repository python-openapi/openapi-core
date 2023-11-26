from base64 import b64decode
from io import BytesIO

from flask import Response
from flask import request
from flask.helpers import send_file

from openapi_core.contrib.flask.views import FlaskOpenAPIView


class PetPhotoView(FlaskOpenAPIView):
    OPENID_LOGO = b64decode(
        """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
    )

    def get(self, petId):
        fp = BytesIO(self.OPENID_LOGO)
        return send_file(fp, mimetype="image/gif")

    def post(self, petId):
        assert request.data == self.OPENID_LOGO
        return Response(status=201)
