import asyncio
import os
from dotenv import load_dotenv
from src.workflows.story_flow import StoryFlow
from config.database import init_db, SessionLocal
from src.repositories.story_repository import StoryRepository
from src.models.database import StoryStatusEnum

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

async def generate_story(flow):
    """Generate a new story."""
    topic = input("Enter the topic for the story: ")
    try:
        age = float(input("Enter the age of the child: "))
        # Run the async flow
        story = await flow.run(topic, age)
        print(f"\n✓ Story '{story.title}' generated with {len(story.pages)} pages.")
        print(f"✓ Story ID: {story.story_id}")
        print(f"Check the 'outputs/{story.story_id}' directory for files.")
        return story
    except ValueError:
        print("Invalid age entered.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

async def view_stories():
    """View all stories from database."""
    db = SessionLocal()
    repo = StoryRepository(db)
    
    try:
        stories = repo.get_all_stories(limit=20)
        if not stories:
            print("\nNo stories found in database.")
            return
        
        print("\n" + "="*80)
        print("SAVED STORIES")
        print("="*80)
        for idx, story in enumerate(stories, 1):
            print(f"\n{idx}. {story.title}")
            print(f"   ID: {story.story_id}")
            print(f"   Topic: {story.topic} | Age: {story.age_group} years")
            print(f"   Status: {story.status.value} | Pages: {story.total_pages}")
            print(f"   Created: {story.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    finally:
        db.close()

async def view_story_details():
    """View detailed information about a specific story."""
    story_id = input("Enter the Story ID: ")
    db = SessionLocal()
    repo = StoryRepository(db)
    
    try:
        db_story = repo.get_story(story_id)
        if not db_story:
            print(f"\n⚠ Story '{story_id}' not found.")
            return
        
        # Convert to dataclass for easier access
        story = repo.story_to_dataclass(db_story)
        
        print("\n" + "="*80)
        print(f"STORY: {story.title}")
        print("="*80)
        print(f"ID: {story.story_id}")
        print(f"Topic: {story.topic}")
        print(f"Age Group: {story.age_group} years")
        print(f"Status: {story.status.value}")
        print(f"Total Pages: {story.total_pages}")
        print(f"Created: {story.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n{'-'*80}")
        print("PAGES:")
        print(f"{'-'*80}")
        
        for page in story.pages:
            print(f"\nPage {page.page_number}:")
            print(f"Text: {page.text}")
            if page.image_path:
                print(f"Image: {page.image_path}")
            if page.audio_path:
                print(f"Audio: {page.audio_path}")
        
        print("="*80)
    finally:
        db.close()

async def main():
    print("="*80)
    print("KIDS STORY AND IMAGE GENERATOR")
    print("Agentic Workflow with Database Persistence")
    print("="*80)
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    # Initialize database
    print("\nInitializing database...")
    init_db()
    
    flow = StoryFlow(api_key, use_db=True)

    while True:
        print("\n" + "-"*80)
        print("MENU:")
        print("-"*80)
        print("1. Generate New Story (Text + Images + Audio)")
        print("2. View All Saved Stories")
        print("3. View Story Details")
        print("4. Exit")
        print("-"*80)
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            await generate_story(flow)
        
        elif choice == '2':
            await view_stories()
        
        elif choice == '3':
            await view_story_details()
        
        elif choice == '4':
            print("\nExiting. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())


    
    
