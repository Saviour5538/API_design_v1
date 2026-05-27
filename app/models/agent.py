from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.database import Base

class Agent(Base):
    __tablename__ = "nodes"

    id = Column(PGUUID(as_uuid=False), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(PGUUID(as_uuid=False), nullable=True)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    configs = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
