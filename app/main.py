from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

from app.models.category import Category
from app.models.agent import Agent
from app.models.workflow import Workflow
from app.models.workflow_data import WorkflowData
from app.models.execution import Execution
from app.models.node_execution import NodeExecution
from app.models.execution_join_counter import ExecutionJoinCounter

Base.metadata.create_all(bind=engine)

from app.routers import categories, agents, workflows, nodes, executions, edges

app = FastAPI(
    title="Workflow Builder API",
    description="API for managing AI agent workflows",
    version="1.0.0",
    debug=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health", tags=["Health"])
def health():
    return {"status": "success", "data": {"server": "online", "version": "v1"}}

app.include_router(categories.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(nodes.router, prefix="/api/v1")
app.include_router(edges.router, prefix="/api/v1")
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
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Local development"}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
