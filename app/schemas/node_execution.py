from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List

class NodeExecutionOut(BaseModel):
    id: str
    workflow_node_id: str
    status: str
    input_snapshot: Optional[Any]
    output_snapshot: Optional[Any]
    error_log: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
