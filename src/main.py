import os
import asyncio
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging

from . import config
from .llm import LLMFactory
from .image_generator import generate_avatar_image
from .audio_generator import generate_voiceover
from .video_generator import create_ai_influencer_video
from .progress import create_sse_update

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# Mount output directory to serve generated files
app.mount("/output", StaticFiles(directory=config.OUTPUT_DIR), name="output")

# Setup templates
templates = Jinja2Templates(directory=config.ROOT_DIR / "templates")

class GenerationRequest(BaseModel):
    characterstics: str
    script: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/generate")
async def generate_video(request: Request):
    """
    Handles the video generation pipeline and streams progress updates.
    """
    character_description = request.query_params.get("characterstics")
    script = request.query_params.get("script")

    if not character_description or not script:
        raise HTTPException(status_code=400, detail="Missing 'characterstics' or 'script' query parameters.")

    async def event_stream():
        try:
            logger.info("Starting video generation stream.")
            start_time = time.time()
            
            # Stage 1: Generate Image Prompt
            yield create_sse_update(10, "Generating image prompt...", "prompt", "in_progress")
            llm = LLMFactory()
            image_prompt = llm.get_image_prompt(character_description)
            logger.info(f"Image prompt: {image_prompt}")
            yield create_sse_update(25, "Image prompt generated.", "prompt", "complete")

            # Stage 2: Generate Avatar Image
            yield create_sse_update(25, "Generating avatar image...", "image", "in_progress")
            avatar_image_path = await asyncio.to_thread(generate_avatar_image, image_prompt)
            logger.info(f"Avatar image saved to: {avatar_image_path}")
            yield create_sse_update(50, "Avatar image generated.", "image", "complete")

            # Stage 3: Generate Voiceover
            yield create_sse_update(50, "Generating voiceover...", "audio", "in_progress")
            audio_path = await asyncio.to_thread(generate_voiceover, script)
            logger.info(f"Voiceover saved to: {audio_path}")
            yield create_sse_update(75, "Voiceover generated.", "audio", "complete")

            # Stage 4: Create Final Video
            yield create_sse_update(75, "Generating final video...", "video", "in_progress")
            video_path = await asyncio.to_thread(create_ai_influencer_video, avatar_image_path, audio_path)
            logger.info(f"Final video saved to: {video_path}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Send a message with the path to the video
            video_url = f"/output/videos/{video_path.name}"
            yield create_sse_update(100, video_url, "video", "complete", total_time=total_time)

        except Exception as e:
            logger.error(f"An error occurred during video generation: {e}", exc_info=True)
            error_message = create_sse_update(0, f"Error: {e}", "error", "error")
            yield error_message

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/output/videos/{video_name}")
async def get_generated_video(video_name: str):
    """Serves the generated video file."""
    video_path = config.OUTPUT_DIR / "videos" / video_name
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 