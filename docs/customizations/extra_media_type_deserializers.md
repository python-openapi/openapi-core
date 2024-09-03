# Media type deserializers

OpenAPI comes with a set of built-in media type deserializers such as: `application/json`, `application/xml`, `application/x-www-form-urlencoded` or `multipart/form-data`.

You can also define your own ones. Pass custom defined media type deserializers dictionary with supported mimetypes as a key to `unmarshal_response` function:

``` python hl_lines="11"
def protobuf_deserializer(message):
    feature = route_guide_pb2.Feature()
    feature.ParseFromString(message)
    return feature

extra_media_type_deserializers = {
    'application/protobuf': protobuf_deserializer,
}

config = Config(
    extra_media_type_deserializers=extra_media_type_deserializers,
)
openapi = OpenAPI.from_file_path('openapi.json', config=config)

result = openapi.unmarshal_response(request, response)
```
