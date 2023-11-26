from json import dumps

from flask.testing import FlaskClient
from flask.wrappers import Response

from openapi_core import V30RequestUnmarshaller
from openapi_core.contrib.flask import FlaskOpenAPIRequest


class TestFlaskOpenAPIValidation:
    def test_request_validator_root_path(self, schema_path, app_factory):
        def details_view_func(id):
            from flask import request

            openapi_request = FlaskOpenAPIRequest(request)
            unmarshaller = V30RequestUnmarshaller(schema_path)
            result = unmarshaller.unmarshal(openapi_request)
            assert not result.errors

            if request.args.get("q") == "string":
                return Response(
                    dumps({"data": "data"}),
                    headers={"X-Rate-Limit": "12"},
                    mimetype="application/json",
                    status=200,
                )
            else:
                return Response("Not Found", status=404)

        app = app_factory(root_path="/browse")
        app.add_url_rule(
            "/<id>/",
            view_func=details_view_func,
            methods=["POST"],
        )
        query_string = {
            "q": "string",
        }
        headers = {"content-type": "application/json"}
        data = {"param1": 1}
        client = FlaskClient(app)
        result = client.post(
            "/12/",
            base_url="http://localhost/browse",
            query_string=query_string,
            json=data,
            headers=headers,
        )

        assert result.status_code == 200
        assert result.json == {"data": "data"}
