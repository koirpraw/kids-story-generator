import wave
import os

def save_wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Saves PCM data to a WAV file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def save_image(image, filename):
    """Saves a PIL Image to a file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    image.save(filename)
