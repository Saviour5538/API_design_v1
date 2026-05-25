from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: f"agt_{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    inputs = Column(JSON, nullable=False, default=list)
    n8n_workflow_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="agents")
    nodes = relationship("Node", back_populates="agent")
