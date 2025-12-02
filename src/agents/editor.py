from google.adk.agents import Agent
from typing import List, Dict
import json

class EditorAgent:
    """
    EditorAgent is responsible for:
    1. Analyzing the complete story text
    2. Splitting it into well-structured pages
    3. Generating illustration prompts for each page
    4. Ensuring age-appropriate pacing and content
    """
    
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        self.model_name = model_name
        self.agent = self._build_agent()

    def _build_agent(self):
        """Build the editor agent that structures stories into pages."""
        editor_agent = Agent(
            name="EditorAgent",
            model=self.model_name,
            instruction="""You are a children's book editor. Your task is to analyze a story provided by the user and structure it into pages.

Your tasks:
1. Split the story into 4-8 pages (depending on story length and target age)
2. Each page should:
   - Be 2-4 sentences long (adjust based on age mentioned by user: younger = shorter)
   - Represent a clear scene or moment
   - Be suitable for illustration
   - Maintain story flow and pacing
   - End with a natural pause or transition

3. For each page, generate:
   - The page text (extracted/slightly edited from the story)
   - A vivid, detailed illustration prompt describing the scene
   - The illustration prompt should be child-friendly, colorful, and descriptive

Output Format: Return ONLY valid JSON with this structure:
{
  "pages": [
    {
      "page_number": 1,
      "text": "Page text here...",
      "illustration_prompt": "A detailed description for the illustrator..."
    }
  ]
}

CRITICAL: Output ONLY valid JSON, no other text or explanation.""",
        )
        return editor_agent

    def parse_structured_pages(self, json_output: str) -> List[Dict]:
        """Parse the JSON output from the editor agent."""
        try:
            # Clean up potential markdown code blocks
            cleaned = json_output.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            return data.get("pages", [])
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from editor agent: {e}")
            print(f"Raw output: {json_output}")
            # Fallback: return empty list
            return []
