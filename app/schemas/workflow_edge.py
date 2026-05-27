from pydantic import BaseModel
from datetime import datetime
from typing import List

class EdgeCreate(BaseModel):
    src_id: str
    dest_id: str

class EdgeOut(BaseModel):
    id: str
    src_id: str
    dest_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class EdgeListOut(BaseModel):
    items: List[EdgeOut]
    total: int
