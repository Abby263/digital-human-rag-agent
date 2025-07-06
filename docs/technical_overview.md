# Technical Overview: Digital Human Generator

This document provides a detailed technical explanation of the Digital Human Generator application, from initial user input to the final generated video.

## System Architecture

The application is built on a modular, asynchronous pipeline using FastAPI for the web server and a series of specialized AI models for each stage of the generation process. The backend is designed to be run locally and is optimized for different hardware, including Apple Silicon (MPS) and NVIDIA GPUs (CUDA).

```mermaid
graph TD
    subgraph Frontend
        A[HTML/CSS/JS Interface]
    end

    subgraph Backend (FastAPI)
        B[Web Server: main.py]
        C[SSE Endpoint: /generate]
    end

    subgraph AI Pipeline
        D[LLM: llm.py]
        E[Image Gen: image_generator.py]
        F[Audio Gen: audio_generator.py]
        G[Video Gen: video_generator.py]
    end

    subgraph Models
        H[Ollama: gemma:2b]
        I[Hugging Face: Stable Diffusion]
        J[gTTS: Google Text-to-Speech]
        K[SadTalker & GFPGAN]
    end
    
    A -- HTTP Request --> B
    B -- Calls --> C
    C -- Streams Progress --> A
    
    C -- Invokes --> D
    D -- Uses --> H
    D -- Returns Prompt --> C
    
    C -- Invokes --> E
    E -- Uses --> I
    E -- Returns Image --> C
    
    C -- Invokes --> F
    F -- Uses --> J
    F -- Returns Audio --> C
    
    C -- Invokes --> G
    G -- Uses --> K
    G -- Returns Video --> C
```

## Step-by-Step Generation Flow

The video creation process is a sequence of four main stages, orchestrated by the `generate_video` function in `src/main.py` and streamed to the user via Server-Sent Events (SSE).

### 1. Stage 1: Prompt Generation

-   **Trigger**: The user submits the character description and script via the web form.
-   **File**: `src/llm.py`
-   **Model**: `Ollama gemma:2b`
-   **Process**:
    1.  The `LLMFactory` takes the user's brief character description (e.g., "A confident CEO").
    2.  It uses a `langchain` prompt template (`prompts/image_prompt.txt`) to construct a detailed query for the LLM.
    3.  Crucially, it injects specific instructions to generate a prompt for a **passport-style, front-facing headshot**, which is the ideal input for the video generation stage.
    4.  The `gemma:2b` model processes this and returns a detailed, single-sentence prompt suitable for Stable Diffusion (e.g., "A photorealistic, 4k, passport-style photograph of a confident female CEO...").

### 2. Stage 2: Avatar Image Creation

-   **Trigger**: The detailed image prompt from Stage 1 is received.
-   **File**: `src/image_generator.py`
-   **Model**: `stabilityai/stable-diffusion-2-1-base`
-   **Process**:
    1.  The `generate_avatar_image` function initializes the `DiffusionPipeline` from Hugging Face.
    2.  **Hardware Optimization**: It detects the available hardware (MPS, CUDA, or CPU) and configures the pipeline accordingly.
        -   On **Apple Silicon (MPS)**, it uses `torch.float32` and other specific workarounds to prevent common "black image" or `NaN` errors, ensuring stable GPU-accelerated performance.
        -   If MPS fails, it automatically **falls back to CPU** to ensure the generation completes.
    3.  The Stable Diffusion model generates a 512x512 image based on the prompt.
    4.  The final image is saved to `output/images/source_image.png`.

### 3. Stage 3: Voiceover Synthesis

-   **Trigger**: The avatar image is successfully generated.
-   **File**: `src/audio_generator.py`
-   **Model**: `gTTS` (Google Text-to-Speech)
-   **Process**:
    1.  The user's original script is passed to the `generate_voiceover` function.
    2.  `gTTS` converts the text into an MP3 audio file in memory.
    3.  `ffmpeg` is used to convert the MP3 into a **16000 Hz mono WAV file**, which is the required format for the lip-sync model.
    4.  The final audio is saved to `output/audio/audio.wav`.

### 4. Stage 4: Lip-Synced Video Rendering

-   **Trigger**: Both the image and audio files are ready.
-   **File**: `src/video_generator.py`
-   **Model**: `SadTalker`
-   **Process**:
    1.  The `create_ai_influencer_video` function calls the `SadTalker/inference.py` script as a subprocess.
    2.  It passes the **absolute paths** to the generated image and audio files.
    3.  SadTalker's deep learning model analyzes the audio to predict facial muscle movements (lip sync, blinking, and head motion).
    4.  It deconstructs the source image into 3D facial landmarks and then animates these landmarks frame by frame to match the predicted movements.
    5.  The `GFPGAN` enhancer is used to improve the quality of the animated face in each frame.
    6.  The frames are stitched together into a final MP4 video.
    7.  The video is initially saved in `output/temp_results` and then moved to `output/videos/generated_video.mp4`.
    8.  The application serves this final file to the user.

This detailed, multi-stage process ensures that each component is optimized for its specific task, resulting in a high-quality, AI-generated digital human video. 