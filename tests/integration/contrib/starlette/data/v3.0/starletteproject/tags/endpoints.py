from starlette.responses import Response


async def tag_list_endpoint(request):
    assert request.scope["openapi"]
    assert not request.scope["openapi"].errors
    assert request.method == "GET"
    headers = {
        "X-Rate-Limit": "12",
    }
    return Response(status_code=201, headers=headers)
