from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool
from src.models.story import Story
import os

# This is the function that the RefinerAgent will call to exit the loop.
def exit_loop():
    """Call this function ONLY when the critique is 'APPROVED', indicating the story is finished and no more changes are needed."""
    return {"status": "approved", "message": "Story approved. Exiting refinement loop."}

class WriterAgent:
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        self.model_name = model_name
        self.agent = self._build_agent()

    def _build_agent(self):
        initial_writer_agent = Agent(
            name="InitialWriterAgent",
            model=self.model_name,
            instruction="""Based on the user's prompt, write the first draft of a short story (around 100-150 words).
            Output only the story text, with no introduction or explanation.""",
            output_key="current_story",
        )

        critic_agent = Agent(
            name="CriticAgent",
            model=self.model_name,
            instruction="""You are a constructive story critic. Review the story provided below.
            Story: {current_story}
            
            Evaluate the story's plot, characters, and pacing.
            - If the story is well-written and complete, you MUST respond with the exact phrase: "APPROVED"
            - Otherwise, provide 2-3 specific, actionable suggestions for improvement.""",
            output_key="critique",
        )

        refiner_agent = Agent(
            name="RefinerAgent",
            model=self.model_name,
            instruction="""You are a story refiner. You have a story draft and critique.
            
            Story Draft: {current_story}
            Critique: {critique}
            
            Your task is to analyze the critique.
            - IF the critique is EXACTLY "APPROVED", you MUST call the `exit_loop` function and nothing else.
            - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.""",
            output_key="current_story",
            tools=[FunctionTool(exit_loop)],
        )

        story_refinement_loop = LoopAgent(
            name="StoryRefinementLoop",
            sub_agents=[critic_agent, refiner_agent],
            max_iterations=2,
        )

        root_agent = SequentialAgent(
            name="StoryPipeline",
            sub_agents=[initial_writer_agent, story_refinement_loop],
        )
        
        return root_agent

    def write_story(self, runner, prompt: str) -> str:
        # This method assumes the runner is passed in or managed externally
        # For now, we return the agent structure to be run by the orchestrator
        pass
