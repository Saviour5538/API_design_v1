from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any, Dict

class ExecutionWorkflowOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class ExecutionCreate(BaseModel):
    workflow_id: str
    input_variables: Optional[Dict[str, Any]] = {}

class ExecutionOut(BaseModel):
    id: str
    workflow: ExecutionWorkflowOut
    status: str
    input_variables: Optional[Dict[str, Any]]
    output_variables: Optional[Any]
    started_at: datetime
    finished_at: Optional[datetime]
    created_at: datetime
    node_executions: List[Any] = []

    class Config:
        from_attributes = True

class ExecutionListOut(BaseModel):
    items: List[ExecutionOut]
    total: int
    page: int
    limit: int
    total_pages: int
