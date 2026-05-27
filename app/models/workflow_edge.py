from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from app.database import Base

class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"

    id = Column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    src_id = Column(PGUUID(as_uuid=False), ForeignKey("workflow_nodes.id"), nullable=False)
    dest_id = Column(PGUUID(as_uuid=False), ForeignKey("workflow_nodes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    src_node = relationship("Node", foreign_keys=[src_id])
    dest_node = relationship("Node", foreign_keys=[dest_id])
