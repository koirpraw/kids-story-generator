"""
SQLAlchemy ORM models for database persistence.
Maps to SQLite database tables.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum

class StoryStatusEnum(enum.Enum):
    """Story status enumeration."""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

class AssetTypeEnum(enum.Enum):
    """Asset type enumeration."""
    IMAGE = "image"
    AUDIO = "audio"
    COVER = "cover"

class StoryDB(Base):
    """
    Story table - stores story metadata.
    """
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    story_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    topic = Column(String(500), nullable=False)
    age_group = Column(Float, nullable=False)
    status = Column(SQLEnum(StoryStatusEnum), default=StoryStatusEnum.DRAFT, nullable=False)
    total_pages = Column(Integer, default=0)
    cover_image_path = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    pages = relationship("PageDB", back_populates="story", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Story(id={self.id}, story_id='{self.story_id}', title='{self.title}')>"

class PageDB(Base):
    """
    Page table - stores individual story pages.
    """
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    story_id = Column(String(255), ForeignKey("stories.story_id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    text = Column(String(5000), nullable=False)
    image_prompt = Column(String(2000), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    story = relationship("StoryDB", back_populates="pages")
    assets = relationship("AssetDB", back_populates="page", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Page(id={self.id}, story_id='{self.story_id}', page_number={self.page_number})>"

class AssetDB(Base):
    """
    Asset table - stores file paths for images and audio files.
    """
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    asset_type = Column(SQLEnum(AssetTypeEnum), nullable=False)
    file_path = Column(String(1000), nullable=False)
    cloud_url = Column(String(2000), nullable=True)  # For future cloud storage
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    page = relationship("PageDB", back_populates="assets")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, page_id={self.page_id}, type='{self.asset_type.value}')>"
