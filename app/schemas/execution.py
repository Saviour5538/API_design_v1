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
    input_values: Optional[Dict[str, Any]] = {}

class WebhookUpdate(BaseModel):
    n8n_execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ExecutionOut(BaseModel):
    execution_id: str
    workflow: ExecutionWorkflowOut
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[Any]
    error: Optional[str]

    class Config:
        from_attributes = True

class ExecutionListOut(BaseModel):
    items: List[ExecutionOut]
    total: int
    page: int
    limit: int
    total_pages: int
