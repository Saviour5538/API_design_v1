from pydantic import BaseModel
from typing import List

class EdgeCreate(BaseModel):
    src_id: str
    dest_id: str

class EdgeOut(BaseModel):
    id: str
    src_id: str
    dest_id: str

class EdgeListOut(BaseModel):
    items: List[EdgeOut]
    total: int
