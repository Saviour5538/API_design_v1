from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class WorkflowListItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    version: int
    node_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowDetailOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    version: int
    nodes: List[Any] = []
    edges: List[Any] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowListOut(BaseModel):
    items: List[WorkflowListItemOut]
    total: int
    page: int
    limit: int
    total_pages: int
