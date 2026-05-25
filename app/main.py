from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine

# Import ALL models explicitly before create_all so every table is registered
from app.models.user import User
from app.models.category import Category
from app.models.agent import Agent
from app.models.workflow import Workflow
from app.models.node import Node
from app.models.execution import Execution

Base.metadata.create_all(bind=engine)

from app.routers import auth, categories, agents, workflows, nodes, executions

app = FastAPI(
    title="Workflow Builder API",
    description="API for managing AI agent workflows",
    version="1.0.0",
    debug=True
)

@app.get("/api/v1/health", tags=["Health"])
def health():
    return {"status": "success", "data": {"server": "online", "version": "v1"}}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(nodes.router, prefix="/api/v1")
app.include_router(executions.router, prefix="/api/v1")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Workflow Builder API",
        version="1.0.0",
        description="API for managing AI agent workflows",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    openapi_schema["servers"] = [
        {"url": "https://workflow.aifirstenteprise.ai", "description": "Production"},
        {"url": "http://localhost:8000", "description": "Local development"}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
