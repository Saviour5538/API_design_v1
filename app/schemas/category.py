from pydantic import BaseModel
from typing import Optional, List

class CategoryCreate(BaseModel):
    name: str
    color: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class CategoryOut(BaseModel):
    id: str
    name: str
    color: Optional[str]
    agent_count: int = 0

    class Config:
        from_attributes = True

class CategoryListOut(BaseModel):
    items: List[CategoryOut]
    total: int
    page: int
    limit: int
    total_pages: int
