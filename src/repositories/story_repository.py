"""
Repository layer for Story database operations.
Implements CRUD operations and business logic for story persistence.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.database import StoryDB, PageDB, AssetDB, StoryStatusEnum, AssetTypeEnum
from src.models.story import Story, Page, StoryStatus
from datetime import datetime
import os

class StoryRepository:
    """Repository for Story-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_story(self, story: Story) -> StoryDB:
        """
        Create a new story in the database.
        
        Args:
            story: Story dataclass instance
            
        Returns:
            StoryDB: Created database record
        """
        # Map dataclass status to enum
        status_map = {
            StoryStatus.DRAFT: StoryStatusEnum.DRAFT,
            StoryStatus.GENERATING: StoryStatusEnum.GENERATING,
            StoryStatus.COMPLETED: StoryStatusEnum.COMPLETED,
            StoryStatus.FAILED: StoryStatusEnum.FAILED,
            StoryStatus.ARCHIVED: StoryStatusEnum.ARCHIVED,
        }
        
        db_story = StoryDB(
            story_id=story.story_id,
            title=story.title,
            topic=story.topic,
            age_group=story.age_group,
            status=status_map.get(story.status, StoryStatusEnum.DRAFT),
            total_pages=len(story.pages),
            cover_image_path=story.cover_image_path,
            created_at=story.created_at or datetime.now(),
            updated_at=story.updated_at or datetime.now()
        )
        
        self.db.add(db_story)
        self.db.commit()
        self.db.refresh(db_story)
        
        return db_story
    
    def save_page(self, story_id: str, page: Page) -> PageDB:
        """
        Save a page to the database.
        
        Args:
            story_id: Story identifier
            page: Page dataclass instance
            
        Returns:
            PageDB: Created page record
        """
        db_page = PageDB(
            story_id=story_id,
            page_number=page.page_number,
            text=page.text,
            image_prompt=page.image_prompt,
            created_at=page.created_at or datetime.now()
        )
        
        self.db.add(db_page)
        self.db.commit()
        self.db.refresh(db_page)
        
        # Save assets if they exist
        if page.image_path:
            self.save_asset(db_page.id, AssetTypeEnum.IMAGE, page.image_path)
        if page.audio_path:
            self.save_asset(db_page.id, AssetTypeEnum.AUDIO, page.audio_path)
        
        return db_page
    
    def save_asset(self, page_id: int, asset_type: AssetTypeEnum, file_path: str) -> AssetDB:
        """
        Save an asset (image or audio) to the database.
        
        Args:
            page_id: Database ID of the page
            asset_type: Type of asset (IMAGE or AUDIO)
            file_path: Path to the asset file
            
        Returns:
            AssetDB: Created asset record
        """
        size_bytes = None
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
        
        db_asset = AssetDB(
            page_id=page_id,
            asset_type=asset_type,
            file_path=file_path,
            size_bytes=size_bytes,
            created_at=datetime.now()
        )
        
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)
        
        return db_asset
    
    def save_complete_story(self, story: Story) -> StoryDB:
        """
        Save a complete story with all pages and assets.
        
        Args:
            story: Complete Story dataclass instance
            
        Returns:
            StoryDB: Created story record
        """
        # Create story record
        db_story = self.create_story(story)
        
        # Save all pages
        for page in story.pages:
            self.save_page(story.story_id, page)
        
        return db_story
    
    def get_story(self, story_id: str) -> Optional[StoryDB]:
        """
        Retrieve a story by its ID.
        
        Args:
            story_id: Story identifier
            
        Returns:
            StoryDB or None
        """
        return self.db.query(StoryDB).filter(StoryDB.story_id == story_id).first()
    
    def get_all_stories(self, limit: int = 100) -> List[StoryDB]:
        """
        Retrieve all stories, most recent first.
        
        Args:
            limit: Maximum number of stories to return
            
        Returns:
            List of StoryDB records
        """
        return (
            self.db.query(StoryDB)
            .order_by(StoryDB.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_stories_by_status(self, status: StoryStatusEnum) -> List[StoryDB]:
        """
        Retrieve stories by status.
        
        Args:
            status: Story status to filter by
            
        Returns:
            List of StoryDB records
        """
        return (
            self.db.query(StoryDB)
            .filter(StoryDB.status == status)
            .order_by(StoryDB.created_at.desc())
            .all()
        )
    
    def get_pages(self, story_id: str) -> List[PageDB]:
        """
        Retrieve all pages for a story.
        
        Args:
            story_id: Story identifier
            
        Returns:
            List of PageDB records ordered by page number
        """
        return (
            self.db.query(PageDB)
            .filter(PageDB.story_id == story_id)
            .order_by(PageDB.page_number)
            .all()
        )
    
    def update_story_status(self, story_id: str, status: StoryStatusEnum) -> bool:
        """
        Update the status of a story.
        
        Args:
            story_id: Story identifier
            status: New status
            
        Returns:
            bool: True if successful
        """
        db_story = self.get_story(story_id)
        if db_story:
            db_story.status = status
            db_story.updated_at = datetime.now()
            self.db.commit()
            return True
        return False
    
    def delete_story(self, story_id: str) -> bool:
        """
        Delete a story and all associated pages and assets.
        
        Args:
            story_id: Story identifier
            
        Returns:
            bool: True if successful
        """
        db_story = self.get_story(story_id)
        if db_story:
            self.db.delete(db_story)
            self.db.commit()
            return True
        return False
    
    def story_to_dataclass(self, db_story: StoryDB) -> Story:
        """
        Convert database Story to dataclass Story.
        
        Args:
            db_story: StoryDB instance
            
        Returns:
            Story dataclass instance
        """
        # Map database enum to dataclass enum
        status_map = {
            StoryStatusEnum.DRAFT: StoryStatus.DRAFT,
            StoryStatusEnum.GENERATING: StoryStatus.GENERATING,
            StoryStatusEnum.COMPLETED: StoryStatus.COMPLETED,
            StoryStatusEnum.FAILED: StoryStatus.FAILED,
            StoryStatusEnum.ARCHIVED: StoryStatus.ARCHIVED,
        }
        
        story = Story(
            title=db_story.title,
            topic=db_story.topic,
            age_group=db_story.age_group,
            status=status_map.get(db_story.status, StoryStatus.DRAFT),
            story_id=db_story.story_id,
            cover_image_path=db_story.cover_image_path,
            created_at=db_story.created_at,
            updated_at=db_story.updated_at
        )
        
        # Load pages
        db_pages = self.get_pages(db_story.story_id)
        for db_page in db_pages:
            # Get assets for this page
            image_path = None
            audio_path = None
            
            for asset in db_page.assets:
                if asset.asset_type == AssetTypeEnum.IMAGE:
                    image_path = asset.file_path
                elif asset.asset_type == AssetTypeEnum.AUDIO:
                    audio_path = asset.file_path
            
            page = Page(
                page_number=db_page.page_number,
                text=db_page.text,
                image_prompt=db_page.image_prompt,
                image_path=image_path,
                audio_path=audio_path,
                created_at=db_page.created_at
            )
            story.pages.append(page)
        
        story.total_pages = len(story.pages)
        return story
