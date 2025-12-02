from google import genai
from google.genai import types
from src.utils.file_io import save_image
import os

class IllustratorAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_image(self, prompt: str, output_path: str):
        print(f"Generating image for prompt: {prompt}")
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
        )
        
        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                save_image(image, output_path)
                return output_path
            elif part.text is not None:
                 # Handle case where model refuses or returns text
                 print(f"Model returned text instead of image: {part.text}")
        return None
