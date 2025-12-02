from google import genai
from google.genai import types
from src.utils.file_io import save_wave_file
import os

class NarratorAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_audio(self, text: str, output_path: str):
        print(f"Generating audio for text: {text[:50]}...")
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=[text],
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore")
                    )
                )
            )
        )
        
        # Check if we have candidates and content
        if response.candidates and response.candidates[0].content.parts:
             data = response.candidates[0].content.parts[0].inline_data.data
             save_wave_file(output_path, data)
             return output_path
        return None
