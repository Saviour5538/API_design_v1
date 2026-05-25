from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any

class WorkflowCategoryOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class WorkflowUserOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[str] = None

class WorkflowListItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    category: Optional[WorkflowCategoryOut]
    node_count: int = 0
    created_by: WorkflowUserOut
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowDetailOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    category: Optional[WorkflowCategoryOut]
    nodes: List[Any] = []
    created_by: WorkflowUserOut
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
