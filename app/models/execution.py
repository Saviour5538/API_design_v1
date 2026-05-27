from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from app.database import Base

class Execution(Base):
    __tablename__ = "workflow_executions"

    id = Column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(PGUUID(as_uuid=False), ForeignKey("workflows.id"), nullable=False)
    status = Column(String, default="PENDING")
    input_variables = Column(JSON, nullable=True, default=dict)
    output_variables = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workflow = relationship("Workflow", back_populates="executions")
    node_executions = relationship("NodeExecution", back_populates="execution", cascade="all, delete-orphan")
