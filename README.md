# Children Story Generator with Gemini(Google GenAI) and Google-adk

This project is an agentic application that generates children's stories based on user input using Gemini(Google Gen AI) and Google-adk. It orchestrates a workflow to generate story text, illustrations, and audio narration with SQLite database persistence.Gemini-2.5-flash-image and gemini-2.5-flash-preview-tts are used for image and audio generation. Gemini-2.5-flash-lite is used for text generation and refinement.The initial version is a CLI application, with plans for a web-based GUI in the future.The project features modular design, parallel asset generation, and a robust database schema to manage stories and their associated assets.

## Features
- **Agentic Workflow**: Uses `google-adk` to orchestrate specialized agents.
- **Story Generation**: Creates age-appropriate stories based on topic and age.
- **Intelligent Page Structuring**: EditorAgent analyzes stories and creates well-paced pages.
- **Parallel Asset Generation**: Images and audio generated simultaneously for better performance.
- **Illustration**: Generates images for each page/segment using `gemini-2.5-flash-image`.
- **Narration**: Converts story text into speech using `gemini-2.5-flash-preview-tts`.
- **Database Persistence**: SQLite database stores all stories, pages, and asset metadata.
- **Modular Design**: Separated into Writer, Editor, Illustrator, and Narrator agents for easy extensibility.

## Project Structure

```
kids-story-generator/
├── main.py                 # Entry point (CLI)
├── config/
│   ├── __init__.py
│   └── database.py         # Database configuration & initialization
├── src/
│   ├── agents/             # Specialized Agents
│   │   ├── writer.py       # Generates and refines story text
│   │   ├── editor.py       # Structures story into pages
│   │   ├── illustrator.py  # Generates images
│   │   └── narrator.py     # Generates audio
│   ├── models/             # Data models
│   │   ├── story.py        # Story and Page dataclasses
│   │   └── database.py     # SQLAlchemy ORM models
│   ├── repositories/       # Database operations
│   │   └── story_repository.py  # CRUD operations
│   ├── utils/              # Helper functions
│   │   └── file_io.py      # File saving utilities
│   └── workflows/          # Workflow orchestration
│       └── story_flow.py   # Main sequential flow
├── storage/
│   ├── database/           # SQLite database files
│   └── assets/             # Future: persistent asset storage
└── outputs/                # Generated assets (images, audio)
```

## Agentic Workflow Design

### Architecture Overview

This project implements a **multi-agent orchestration pattern** using Google's Agent Development Kit (ADK). The workflow combines several advanced agentic techniques to generate high-quality children's stories with multimedia assets.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STORY GENERATION FLOW                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   User Input│
│ (Topic, Age)│
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 1: STORY GENERATION (Critic-Refiner Loop)                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │   Writer    │─────▶│   Critic    │─────▶│  Refiner    │    │
│  │   Agent     │      │   Agent     │      │   Agent     │    │
│  └─────────────┘      └─────────────┘      └──────┬──────┘    │
│       │                                             │           │
│       │                  ┌──────────────────────────┘           │
│       └──────────────────┤ Approved?                            │
│                          └─── No: Loop back to Writer           │
│                          └─── Yes: Continue ──────────┐         │
└──────────────────────────────────────────────────────┼─────────┘
                                                        │
                                                        ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 2: INTELLIGENT PAGE STRUCTURING                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │           Editor Agent                           │           │
│  │  • Analyzes complete story text                  │           │
│  │  • Splits into 4-8 age-appropriate pages         │           │
│  │  • Generates illustration prompt per page        │           │
│  │  • Ensures narrative pacing and flow             │           │
│  │  • Outputs structured JSON                       │           │
│  └──────────────────────┬───────────────────────────┘           │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
              [Structured Pages with Prompts]
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 3: PARALLEL ASSET GENERATION (Per Page)                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌─────────────────────┐         ┌─────────────────────┐     │
│    │  Illustrator Agent  │         │   Narrator Agent    │     │
│    │  ─────────────────  │         │  ─────────────────  │     │
│    │ • Custom prompt     │         │ • Page text         │     │
│    │ • Age-appropriate   │  ASYNC  │ • Age-appropriate   │     │
│    │ • Colorful style    │ PARALLEL│ • Clear voice       │     │
│    │ • Model:            │ ◄─────► │ • Model:            │     │
│    │   gemini-2.5-flash- │         │   gemini-2.5-flash- │     │
│    │   image             │         │   preview-tts       │     │
│    └──────────┬──────────┘         └──────────┬──────────┘     │
│               │                               │                 │
│               ▼                               ▼                 │
│         [Image File]                    [Audio File]            │
│                                                                  │
│  Technique: ThreadPoolExecutor for concurrent generation        │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  Phase 4: DATABASE PERSISTENCE                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │         SQLite Database (SQLAlchemy ORM)         │           │
│  │  ─────────────────────────────────────────────   │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │           │
│  │  │   Stories   │  │    Pages    │  │  Assets │ │           │
│  │  │   Table     │  │    Table    │  │  Table  │ │           │
│  │  └──────┬──────┘  └──────┬──────┘  └────┬────┘ │           │
│  │         │                │               │      │           │
│  │         └────── 1:N ─────┴───── 1:N ─────┘      │           │
│  │                                                  │           │
│  │  • Story metadata (title, topic, age, status)   │           │
│  │  • Page content and illustration prompts        │           │
│  │  • Asset file paths and metadata                │           │
│  │  • Full CRUD operations via Repository pattern  │           │
│  └──────────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Complete Story │
                 │   with Assets   │
                 └─────────────────┘
```

### Agentic Techniques Applied

#### 1. **Multi-Agent Orchestration**
- **Pattern**: Specialized agents for distinct tasks (Writer, Critic, Refiner, Editor, Illustrator, Narrator)
- **Benefit**: Each agent focuses on a specific domain, improving output quality
- **Implementation**: Google ADK's `Agent` and `SequentialAgent` classes

#### 2. **Critic-Refiner Loop (Self-Reflection)**
- **Pattern**: Iterative improvement through critic feedback
- **Flow**: Writer → Critic evaluates → Refiner improves → Loop until approved
- **Benefit**: Ensures story quality, age-appropriateness, and narrative coherence
- **Termination**: Critic agent outputs "APPROVED" when quality standards are met

#### 3. **Structured Output Generation**
- **Pattern**: Editor agent produces JSON-formatted page structures
- **Technique**: Prompt engineering with explicit output format requirements
- **Validation**: JSON parsing with fallback error handling
- **Benefit**: Reliable, parseable data for downstream processing

#### 4. **Parallel Execution**
- **Pattern**: Concurrent asset generation per page
- **Implementation**: Python's `ThreadPoolExecutor` with `asyncio.gather()`
- **Agents**: Illustrator + Narrator run simultaneously
- **Benefit**: 2x speedup compared to sequential processing

#### 5. **State Management**
- **Pattern**: Database-backed persistence with status tracking
- **States**: DRAFT → GENERATING → COMPLETED / FAILED
- **Repository Pattern**: Clean separation of data access logic
- **Benefit**: Resume failed generations, track progress, retrieve historical data

#### 6. **Prompt Engineering**
- **Technique**: Context-aware, role-based system instructions
- **Examples**:
  - Writer: "Create age-appropriate story with sensory details"
  - Editor: "Split into 4-8 pages with clear scene transitions"
  - Illustrator: "Child-friendly, colorful, descriptive scene"
- **Benefit**: Consistent, high-quality outputs aligned with requirements

#### 7. **Event-Driven Architecture**
- **Pattern**: `InMemoryRunner` processes events from agent execution
- **Event Types**: User messages, model responses, tool calls
- **Processing**: Extract text from `event.content.parts`
- **Benefit**: Fine-grained control over agent interactions

### Agent Responsibilities

| Agent | Model | Role | Output |
|-------|-------|------|--------|
| **WriterAgent** | gemini-2.5-flash-lite | Initial story generation | Raw story text |
| **CriticAgent** | gemini-2.5-flash-lite | Quality evaluation | Feedback or APPROVED |
| **RefinerAgent** | gemini-2.5-flash-lite | Story improvement | Refined story text |
| **EditorAgent** | gemini-2.5-flash-lite | Page structuring | JSON with pages + prompts |
| **IllustratorAgent** | gemini-2.5-flash-image | Image generation | PNG image files |
| **NarratorAgent** | gemini-2.5-flash-preview-tts | Audio generation | MP3 audio files |

### Workflow Execution Steps

The `StoryFlow` (`src/workflows/story_flow.py`) orchestrates the following process:

1.  **Writer Agent (Critic-Refiner Loop)**:
    *   Generates a story draft based on the user's topic and age input.
    *   Critiques and refines the draft using a feedback loop (Writer → Critic → Refiner).
    *   Continues until critic approves the story quality.

2.  **Editor Agent** :
    *   Analyzes the complete story text.
    *   Intelligently splits it into 4-8 age-appropriate pages.
    *   Generates detailed illustration prompts for each page.
    *   Returns structured JSON output.

3.  **Parallel Asset Generation**:
    *   For each page:
        *   **Illustrator Agent** and **Narrator Agent** run in parallel (ThreadPoolExecutor).
        *   Generates illustration based on the custom prompt.
        *   Generates audio narration for the page text.

4.  **Database Persistence**:
    *   Story metadata saved to SQLite database with status tracking.
    *   All pages and asset paths tracked in database.
    *   Stories can be retrieved and viewed later via Repository pattern.

5.  **Output**:
    *   Files are saved in the `outputs/[story_id]/` directory.
    *   Database records stored in `storage/database/stories.db`.
    *   Create outputs folder manually before first generation, generated image and audio files will be saved there.
    *   Create storage folder with `storage/database/` in project root, the database files will be stored there.
  (** make sure these folders exist before first run,else errors may occur **)
 
## Database Schema

**Stories Table:**
- Stores story metadata (title, topic, age, status, timestamps)

**Pages Table:**
- Stores individual page content and prompts
- Links to story via foreign key

**Assets Table:**
- Stores file paths for images and audio
- Links to pages via foreign key
- Tracks file size and type

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```
4. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```
2.  Select from the menu:
    - **Generate New Story**: Create a story with text, images, and audio
    - **View All Saved Stories**: List all stories in the database
    - **View Story Details**: See complete information about a specific story

3. Generated files are organized by story ID in `outputs/[story_id]/`

## Recent Enhancements

### Phase 1: Enhanced Agents ✅
- **EditorAgent**: Intelligent page structuring with custom illustration prompts
- **Parallel Processing**: Image and audio generation run simultaneously per page
- **Enhanced Models**: Added status tracking, timestamps, and metadata

### Phase 2: Database Integration ✅
- **SQLite Database**: Persistent storage with SQLAlchemy ORM
- **Repository Pattern**: Clean separation of data access logic
- **CRUD Operations**: Full Create, Read, Update, Delete support
- **Story Retrieval**: View and browse previously generated stories

## Future Work/Enhancements
-   **GUI**: Implement a web interface using Streamlit or Gradio
-   **Cloud Storage**: Integrate with Google Cloud Storage for asset hosting
-   **PDF Export**: Combine text and images into a printable PDF
-   **Add Human-in-the-Loop**: Allow user edits between stages, improving story quality and relevance.
-   **More styles for illustrations and narrations**: Different artistic styles such as cartoon, watercolor, sketch, etc. Different voice styles for narration.
-   **Interactive Storytelling**: Enable user choices that affect story outcome.
-   **Multilingual Support**: Expand story generation to multiple languages.
-   **Agent deployment/backend hosting**: Deploy agents on cloud platforms for scalability. Make workflow accessible via REST API.

## Python Environement
-   Python 3.12 or higher is required to run this project.
-   use `uv` for package management and dependency resolution(optional)
-   `.venv` for the virtual environment.
-   

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
