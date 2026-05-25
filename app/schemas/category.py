from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    agent_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryListOut(BaseModel):
    items: List[CategoryOut]
    total: int
    page: int
    limit: int
    total_pages: int
