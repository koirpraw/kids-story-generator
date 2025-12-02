from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class StoryStatus(Enum):
    """Status of story generation."""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

@dataclass
class Page:
    page_number: int
    text: str
    image_prompt: Optional[str] = None
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Story:
    title: str
    topic: str
    age_group: float
    pages: List[Page] = field(default_factory=list)
    cover_image_path: Optional[str] = None
    status: StoryStatus = StoryStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    story_id: Optional[str] = None  # Unique identifier
    total_pages: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.story_id is None:
            # Generate a simple ID based on topic and timestamp
            timestamp = int(self.created_at.timestamp())
            self.story_id = f"{self.topic.replace(' ', '_')}_{timestamp}"
    
    def add_page(self, text: str, image_prompt: Optional[str] = None):
        """Add a new page to the story."""
        page_num = len(self.pages) + 1
        page = Page(
            page_number=page_num,
            text=text,
            image_prompt=image_prompt
        )
        self.pages.append(page)
        self.total_pages = len(self.pages)
        self.updated_at = datetime.now()
    
    def mark_completed(self):
        """Mark story as completed."""
        self.status = StoryStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def mark_failed(self):
        """Mark story generation as failed."""
        self.status = StoryStatus.FAILED
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert story to dictionary for serialization."""
        return {
            "story_id": self.story_id,
            "title": self.title,
            "topic": self.topic,
            "age_group": self.age_group,
            "status": self.status.value,
            "total_pages": self.total_pages,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "cover_image_path": self.cover_image_path,
            "pages": [
                {
                    "page_number": p.page_number,
                    "text": p.text,
                    "image_prompt": p.image_prompt,
                    "image_path": p.image_path,
                    "audio_path": p.audio_path,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in self.pages
            ]
        }

