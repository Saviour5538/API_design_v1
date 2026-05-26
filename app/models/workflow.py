from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=lambda: f"wfl_{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="draft")  # draft | active | inactive
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category")
    nodes = relationship("Node", back_populates="workflow", order_by="Node.order")
    executions = relationship("Execution", back_populates="workflow")
