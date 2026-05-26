from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, default=lambda: f"exc_{uuid.uuid4().hex[:8]}")
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    status = Column(String, default="running")  # running | completed | failed | cancelled
    input_values = Column(JSON, nullable=True, default=dict)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    n8n_execution_id = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", back_populates="executions")
