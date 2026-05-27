from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from app.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="DRAFT")
    version = Column(Integer, default=1)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    nodes = relationship("Node", back_populates="workflow")
    executions = relationship("Execution", back_populates="workflow")
