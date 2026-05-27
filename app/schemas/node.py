from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NodeConfigIn(BaseModel):
    var_name: str
    value: Optional[str] = None

class NodeConfigOut(BaseModel):
    id: str
    var_name: str
    value: Optional[str]

    class Config:
        from_attributes = True

class NodeAgentOut(BaseModel):
    id: str
    name: str
    category: Optional[str]

    class Config:
        from_attributes = True

class NodeCreate(BaseModel):
    node_id: str
    configs: Optional[List[NodeConfigIn]] = []

class NodeUpdate(BaseModel):
    configs: Optional[List[NodeConfigIn]] = None

class NodeOut(BaseModel):
    id: str
    node_id: str
    agent: NodeAgentOut
    configs: List[NodeConfigOut] = []
    workflow_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NodeListOut(BaseModel):
    items: List[NodeOut]
    total: int
