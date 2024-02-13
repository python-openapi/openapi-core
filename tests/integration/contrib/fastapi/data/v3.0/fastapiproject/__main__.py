from fastapi import FastAPI
from fastapiproject.openapi import openapi
from fastapiproject.routers import pets

from openapi_core.contrib.fastapi.middlewares import FastAPIOpenAPIMiddleware

app = FastAPI()
app.add_middleware(FastAPIOpenAPIMiddleware, openapi=openapi)
app.include_router(pets.router)
