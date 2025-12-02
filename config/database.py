"""
Database configuration and session management for SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
import os

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "database")
DB_PATH = os.path.join(DB_DIR, "stories.db")

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Create SQLite engine
# Using StaticPool for SQLite to avoid threading issues
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
class Base(DeclarativeBase):
    pass

def get_db():
    """
    Dependency function to get database session.
    Usage:
        with get_db() as db:
            # use db session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    from src.models.database import StoryDB, PageDB, AssetDB
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at: {DB_PATH}")

def reset_db():
    """Drop all tables and recreate them. USE WITH CAUTION!"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠ Database reset complete!")
