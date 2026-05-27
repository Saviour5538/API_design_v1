from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from app.database import Base

class Node(Base):
    __tablename__ = "workflow_nodes"

    id = Column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(PGUUID(as_uuid=False), ForeignKey("workflows.id"), nullable=False)
    node_id = Column(PGUUID(as_uuid=False), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workflow = relationship("Workflow", back_populates="nodes")
    configs = relationship("WorkflowNodeConfig", back_populates="workflow_node", cascade="all, delete-orphan")
    ui_meta = relationship("WorkflowUIMeta", back_populates="workflow_node", uselist=False, cascade="all, delete-orphan")
    node_executions = relationship("NodeExecution", back_populates="workflow_node")
