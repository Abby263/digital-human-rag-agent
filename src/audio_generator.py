from gtts import gTTS
import os
from pathlib import Path

from . import config

def generate_voiceover(text: str) -> Path:
    """
    Generates a voiceover from text using gTTS.

    Args:
        text (str): The script text for the voiceover.

    Returns:
        Path: The path to the generated audio file.
    """
    print("Generating voiceover...")
    
    tts = gTTS(text)
    temp_mp3_path = config.STATIC_DIR / "temp.mp3"
    tts.save(temp_mp3_path)
    
    # Ensure the destination directory exists
    audio_path = config.GENERATED_AUDIO_PATH
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    # Use ffmpeg to convert to WAV with the correct sample rate for SadTalker
    command = [
        "ffmpeg",
        "-i", str(temp_mp3_path),
        "-ar", "16000",
        "-ac", "1",
        str(audio_path),
        "-y"
    ]
    os.system(" ".join(command))
    
    os.remove(temp_mp3_path)
    
    print(f"Voiceover saved to {audio_path}")
    return audio_path

if __name__ == '__main__':
    # Example usage
    script = "Hello, I am a digital human. I can speak and move my lips."
    generate_voiceover(script) 