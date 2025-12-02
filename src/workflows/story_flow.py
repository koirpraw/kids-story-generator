from google.adk.runners import InMemoryRunner
from src.agents.writer import WriterAgent
from src.agents.illustrator import IllustratorAgent
from src.agents.narrator import NarratorAgent
from src.agents.editor import EditorAgent
from src.models.story import Story, Page, StoryStatus
from src.repositories.story_repository import StoryRepository
from config.database import SessionLocal
import os
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

class StoryFlow:
    def __init__(self, api_key, use_db: bool = True):
        self.api_key = api_key
        self.writer = WriterAgent()
        self.editor = EditorAgent()
        self.illustrator = IllustratorAgent(api_key)
        self.narrator = NarratorAgent(api_key)
        self.use_db = use_db

    async def _generate_page_assets(self, page: Page, story_id: str) -> Page:
        """Generate both image and audio for a single page in parallel."""
        print(f"  Processing page {page.page_number}...")
        
        # Use ThreadPoolExecutor to run sync operations in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Generate Image
            image_path = os.path.join("outputs", story_id, f"page_{page.page_number}.png")
            
            # Generate Audio
            audio_path = os.path.join("outputs", story_id, f"page_{page.page_number}.wav")
            
            # Run both operations in parallel
            loop = asyncio.get_event_loop()
            image_future = loop.run_in_executor(
                executor,
                self.illustrator.generate_image,
                page.image_prompt or f"Children's book illustration: {page.text[:200]}",
                image_path
            )
            audio_future = loop.run_in_executor(
                executor,
                self.narrator.generate_audio,
                page.text,
                audio_path
            )
            
            # Wait for both to complete
            page.image_path, page.audio_path = await asyncio.gather(image_future, audio_future)
        
        return page

    async def run(self, topic: str, age: float) -> Story:
        print(f"Starting story generation for topic: {topic}, age: {age}")
        print("="*60)
        
        # Create Story Object early for tracking
        story = Story(title=f"A Story about {topic}", topic=topic, age_group=age)
        story.status = StoryStatus.GENERATING
        
        # Save initial story to database if enabled
        db_session = None
        if self.use_db:
            db_session = SessionLocal()
            repo = StoryRepository(db_session)
            try:
                repo.create_story(story)
                print(f"✓ Story '{story.story_id}' created in database")
            except Exception as e:
                print(f"⚠ Database error: {e}")
        
        try:
            # 1. Generate Story Text
            print("\n[Phase 1/4] Generating story text...")
            # Generate story text
            prompt = f"Write a short story for a {age} year old child about {topic}."
            runner = InMemoryRunner(agent=self.writer.agent)
            events = await runner.run_debug(user_messages=prompt)
            
            # Extract the story text from events
            story_text = ""
            for event in events:
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            story_text += part.text
            
            if not story_text:
                raise ValueError("Failed to generate story text.")

            print("✓ Story text generated successfully.")
            
            # 2. Structure story into pages using EditorAgent
            print("\n[Phase 2/4] Structuring story into pages...")
            editor_runner = InMemoryRunner(agent=self.editor.agent)
            # Create a detailed prompt that includes the story and age information
            editor_prompt = f"""Please structure this story into 4-8 pages for a {age} year old child.

Story:
{story_text}

Output Format (JSON):
{{
  "pages": [
    {{
      "page_number": 1,
      "text": "Page text here...",
      "illustration_prompt": "A detailed description for the illustrator..."
    }}
  ]
}}

CRITICAL: Output ONLY valid JSON, no other text or explanation."""
            editor_events = await editor_runner.run_debug(user_messages=editor_prompt)
            
            # Extract editor response
            editor_text = ""
            for event in editor_events:
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            editor_text += part.text
            
            if not editor_text:
                raise ValueError("No editor output generated")
            
            pages_data = self.editor.parse_structured_pages(editor_text)
            
            if not pages_data:
                print("⚠ Editor agent failed to structure pages. Falling back to simple split.")
                # Fallback to simple splitting
                paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
                pages_data = [
                    {
                        "page_number": i + 1,
                        "text": p,
                        "illustration_prompt": f"Children's book illustration: {p[:200]}"
                    }
                    for i, p in enumerate(paragraphs)
                ]
            
            print(f"✓ Story structured into {len(pages_data)} pages.")
            
            # 3. Add pages to story
            for page_data in pages_data:
                page = Page(
                    page_number=page_data["page_number"],
                    text=page_data["text"],
                    image_prompt=page_data.get("illustration_prompt", "")
                )
                story.pages.append(page)
            
            story.total_pages = len(story.pages)
            
            # 4. Generate Assets for all pages in parallel
            print(f"\n[Phase 3/4] Generating assets for {len(story.pages)} pages...")
            print("(Images and audio are generated in parallel for each page)")
            
            # Create output directory
            story_id = story.story_id
            os.makedirs(os.path.join("outputs", story_id), exist_ok=True)
            
            # Process all pages - each page's image+audio generated in parallel
            # Pages are processed sequentially to avoid API rate limits
            for page in story.pages:
                await self._generate_page_assets(page, story_id)
                
                # Save page to database after assets are generated
                if self.use_db and db_session:
                    try:
                        repo.save_page(story.story_id, page)
                    except Exception as e:
                        print(f"⚠ Error saving page {page.page_number}: {e}")
                
            print(f"✓ All assets generated successfully.")
            
            # Mark story as completed
            story.mark_completed()
            
            # Update story status in database
            if self.use_db and db_session:
                try:
                    from src.models.database import StoryStatusEnum
                    status_map = {
                        StoryStatus.COMPLETED: StoryStatusEnum.COMPLETED,
                        StoryStatus.FAILED: StoryStatusEnum.FAILED,
                    }
                    db_status = status_map.get(story.status, StoryStatusEnum.COMPLETED)
                    repo.update_story_status(story.story_id, db_status)
                    print(f"✓ Story status updated to: {story.status.value}")
                except Exception as e:
                    print(f"⚠ Error updating story status: {e}")
            
            print("\n[Phase 4/4] Story generation complete!")
            print("="*60)
            return story
            
        except Exception as e:
            # Mark story as failed
            story.mark_failed()
            if self.use_db and db_session:
                try:
                    from src.models.database import StoryStatusEnum
                    repo.update_story_status(story.story_id, StoryStatusEnum.FAILED)
                except:
                    pass
            raise e
        finally:
            if db_session:
                db_session.close()
