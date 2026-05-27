from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base

class Agent(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(String, nullable=True)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    configs = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
