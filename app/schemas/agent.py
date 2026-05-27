from pydantic import BaseModel
from typing import Optional, List, Any, Dict

class AgentCategoryOut(BaseModel):
    id: str
    name: str
    color: Optional[str]

    class Config:
        from_attributes = True

class AgentConfigOut(BaseModel):
    name: Optional[str]
    var_name: Optional[str]
    data_type: Optional[str]

    class Config:
        from_attributes = True

class AgentOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: Optional[AgentCategoryOut]
    input: Optional[Any]
    output: Optional[Any]
    configs: Optional[Any] = []

    class Config:
        from_attributes = True

class AgentListOut(BaseModel):
    items: List[AgentOut]
    total: int
    page: int
    limit: int
    total_pages: int
