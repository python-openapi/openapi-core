---
hide:
  - navigation
---

# Security

Openapi-core provides easy access to security data for authentication and authorization processes.

Supported security schemes:

- http – for Basic and Bearer HTTP authentication schemes
- apiKey – for API keys and cookie authentication

Here's an example with `BasicAuth` and `ApiKeyAuth` security schemes:

```yaml
security:
 - BasicAuth: []
 - ApiKeyAuth: []
components:
 securitySchemes:
   BasicAuth:
     type: http
     scheme: basic
   ApiKeyAuth:
     type: apiKey
     in: header
     name: X-API-Key
```

Security scheme data is accessible from the `security` attribute of the `RequestUnmarshalResult` object.

```python
# Get basic auth decoded credentials
result.security['BasicAuth']

# Get API key
result.security['ApiKeyAuth']
```
