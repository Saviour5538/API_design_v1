from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=lambda: f"nd_{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    input_values = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workflow = relationship("Workflow", back_populates="nodes")
    agent = relationship("Agent", back_populates="nodes")
