from sqlalchemy import Column, String, DateTime
from app.database import Base

class Category(Base):
    __tablename__ = "node_categories"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
