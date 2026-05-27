from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.database import Base

class ExecutionJoinCounter(Base):
    __tablename__ = "execution_join_counters"

    execution_id = Column(PGUUID(as_uuid=False), primary_key=True)
    workflow_node_id = Column(PGUUID(as_uuid=False), primary_key=True)
    remaining_dependencies = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
