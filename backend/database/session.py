from sqlalchemy.orm import sessionmaker, declarative_base
from database.connection import engine

# Create local session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

def get_db():
    """Dependency injection for getting the database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
