from pydantic import BaseModel
from typing import Optional, List

class NodeConfigIn(BaseModel):
    var_name: str
    value: Optional[str] = None

class NodeConfigOut(BaseModel):
    var_name: str
    value: Optional[str]

class UIMeta(BaseModel):
    x: int = 0
    y: int = 0
    label: Optional[str] = None

class NodeAgentOut(BaseModel):
    id: str
    name: str
    category: Optional[str]

class NodeCreate(BaseModel):
    node_id: str
    config: Optional[List[NodeConfigIn]] = []
    ui_meta: Optional[UIMeta] = None

class NodeUpdate(BaseModel):
    config: Optional[List[NodeConfigIn]] = None
    ui_meta: Optional[UIMeta] = None

class NodeOut(BaseModel):
    id: str
    node_id: str
    agent: NodeAgentOut
    config: List[NodeConfigOut] = []
    ui_meta: Optional[UIMeta] = None
    workflow_id: str

class NodeListOut(BaseModel):
    items: List[NodeOut]
    total: int
