from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Resolve SQLite path to absolute so it works regardless of working directory
def resolve_db_url(url: str) -> str:
    if url.startswith("sqlite:///./"):
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_file = url.replace("sqlite:///./", "")
        return f"sqlite:///{os.path.join(project_dir, db_file)}"
    return url

resolved_url = resolve_db_url(settings.DATABASE_URL)
is_sqlite = resolved_url.startswith("sqlite")

engine = create_engine(
    resolved_url,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
