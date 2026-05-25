from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any

class AgentCategoryOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class AgentInput(BaseModel):
    name: str
    type: str
    required: bool

class AgentOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: AgentCategoryOut
    inputs: List[Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AgentDetailOut(AgentOut):
    n8n_workflow_id: Optional[str]

class AgentListOut(BaseModel):
    items: List[AgentOut]
    total: int
    page: int
    limit: int
    total_pages: int
