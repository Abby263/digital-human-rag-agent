import os
from pathlib import Path
import torch
import logging

# Project root
ROOT_DIR = Path(__file__).parent.parent

# Cache directory for models
CACHE_DIR = ROOT_DIR / '.cache'
os.makedirs(CACHE_DIR, exist_ok=True)

# SadTalker
SADTALKER_DIR = ROOT_DIR / 'SadTalker'
SADTALKER_CHECKPOINTS_DIR = SADTALKER_DIR / 'checkpoints'
SADTALKER_GFPGAN_DIR = SADTALKER_DIR / "gfpgan" / "weights"
SADTALKER_INFERENCE_SCRIPT = SADTALKER_DIR / 'inference.py'

# Output directories
OUTPUT_DIR = ROOT_DIR / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generated file paths
GENERATED_IMAGE_PATH = OUTPUT_DIR / "images" / "source_image.png"
GENERATED_AUDIO_PATH = OUTPUT_DIR / "audio" / "audio.wav"
GENERATED_VIDEO_PATH = OUTPUT_DIR / "videos" / "generated_video.mp4"

# --- Static & Temp Dirs ---
STATIC_DIR = ROOT_DIR / "static"
RESULT_DIR = OUTPUT_DIR / "temp_results"
os.makedirs(RESULT_DIR, exist_ok=True)


# LLM Configuration
LLM_MODEL_ID = "gemma:2b"
PROMPTS_DIR = ROOT_DIR / "prompts"
IMAGE_PROMPT_TEMPLATE = (PROMPTS_DIR / "image_prompt.txt").read_text()

# Image Generation
IMAGE_MODEL_ID = "stabilityai/stable-diffusion-2-1-base"
DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = "auto"

# Logging
LOG_LEVEL = logging.INFO 