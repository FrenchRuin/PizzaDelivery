from app.routers.auth_routes import auth_router
from app.routers.order_routes import order_router
from app.routers.page_routes import page_router
from fastapi_jwt_auth import AuthJWT
from app.db.schemas import Settings
from starlette.middleware.cors import CORSMiddleware
import inspect, re, uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi

app = FastAPI()
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(page_router)

# CORS Setting
origins = [
    "http://localhost:8080",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return Settings()


# Swagger UI JWT Token Setting
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Pizza Delivery API",
        version="1.0",
        description="An API for Pizza Delivery Service",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                    re.search("jwt_required", inspect.getsource(endpoint)) or
                    re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                    re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == '__main__':
    uvicorn.run("main:app",host='0.0.0.0', port=8000, reload=True)
