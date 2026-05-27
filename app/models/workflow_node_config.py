from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from app.database import Base

class WorkflowNodeConfig(Base):
    __tablename__ = "workflow_node_configs"

    id = Column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_node_id = Column(PGUUID(as_uuid=False), ForeignKey("workflow_nodes.id"), nullable=False)
    var_name = Column(String, nullable=False)
    value = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workflow_node = relationship("Node", back_populates="configs")
