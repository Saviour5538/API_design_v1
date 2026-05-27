from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.database import Base

class WorkflowUIMeta(Base):
    __tablename__ = "workflow_ui_meta"

    workflow_node_id = Column(PGUUID(as_uuid=False), ForeignKey("workflow_nodes.id"), primary_key=True)
    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workflow_node = relationship("Node", back_populates="ui_meta")
