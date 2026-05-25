from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any, Dict

class NodeAgentOut(BaseModel):
    id: str
    name: str
    category: str

    class Config:
        from_attributes = True

class NodeCreate(BaseModel):
    name: str
    agent_id: str
    order: int
    input_values: Optional[Dict[str, Any]] = {}

class NodeUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None
    input_values: Optional[Dict[str, Any]] = None

class NodeOut(BaseModel):
    id: str
    name: str
    order: int
    agent: NodeAgentOut
    input_values: Dict[str, Any]
    workflow_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NodeListOut(BaseModel):
    items: List[NodeOut]
    total: int
