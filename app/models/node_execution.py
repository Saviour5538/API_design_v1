from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from app.database import Base

class NodeExecution(Base):
    __tablename__ = "node_executions"

    id = Column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(PGUUID(as_uuid=False), ForeignKey("workflow_executions.id"), nullable=False)
    workflow_node_id = Column(PGUUID(as_uuid=False), ForeignKey("workflow_nodes.id"), nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    input_snapshot = Column(JSON, nullable=False, default=dict)
    output_snapshot = Column(JSON, nullable=False, default=dict)
    error_log = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    execution = relationship("Execution", back_populates="node_executions")
    workflow_node = relationship("Node", back_populates="node_executions")
