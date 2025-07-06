# Digital Human RAG Agent

A sophisticated AI-powered application that generates realistic lip-synced videos from character descriptions and scripts. This system combines Large Language Models (LLMs), Stable Diffusion for image generation, text-to-speech synthesis, and SadTalker for video generation to create digital human avatars.

## Features

- **Character Image Generation**: Creates realistic character images from text descriptions using Stable Diffusion
- **Voice Synthesis**: Converts text scripts to natural-sounding speech using text-to-speech models
- **Lip-Sync Video Generation**: Generates realistic lip-synced videos using SadTalker
- **Web Interface**: Simple web interface for easy interaction
- **Modular Architecture**: Clean, maintainable codebase with separate modules for each component

## Architecture

The application consists of several key components:

1. **LLM Module** (`src/llm.py`): Handles language model interactions
2. **Image Generator** (`src/image_generator.py`): Generates character images using Stable Diffusion
3. **Audio Generator** (`src/audio_generator.py`): Converts text to speech
4. **Video Generator** (`src/video_generator.py`): Creates lip-synced videos using SadTalker
5. **Web Interface** (`src/main.py`): Flask-based web application

## Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for faster processing)
- Git LFS (for large model files)
- Poetry (for dependency management)

## Installation

### 1. Clone the Repository

```bash
git clone --recursive https://github.com/yourusername/digital-human-rag-agent.git
cd digital-human-rag-agent
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Download Required Models

The application requires several large model files that are not included in the repository. Run the download script to get all necessary models:

```bash
chmod +x download_models.sh
./download_models.sh
```

This will download approximately 7.6GB of model files:

#### SadTalker Models (~4.1GB)
- `facevid2vid_00189-model.pth.tar` (2.0GB) - Main video generation model
- `SadTalker_V0.0.2_256.safetensors` (705MB) - 256px model
- `SadTalker_V0.0.2_512.safetensors` (704MB) - 512px model
- `epoch_20.pth` (288MB) - Training checkpoint
- `mapping_00109-model.pth.tar` (160MB) - Mapping model
- `mapping_00229-model.pth.tar` (148MB) - Alternative mapping model
- `shape_predictor_68_face_landmarks.dat` (97MB) - Face landmark detector
- `auido2pose_00140-model.pth` (91MB) - Audio to pose model
- `auido2exp_00300-model.pth` (33MB) - Audio to expression model

#### GFPGAN Models (~739MB)
- Face enhancement and restoration models
- Various weight files for different quality levels

#### Additional Models (~1.7GB)
- Stable Diffusion models for image generation
- Text-to-speech models
- Supporting checkpoint files

### 4. Environment Configuration

Create a `.env` file in the root directory with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

## Usage

### Using the Web Interface

1. Start the application:
```bash
make start
```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter a character description and script, then click "Generate Video"

### Using the Command Line

```bash
poetry run python src/main.py
```

### Available Make Commands

```bash
make start    # Start the application
make stop     # Stop the application
make restart  # Restart the application
make clean    # Clean temporary files
```

## Model Details

### SadTalker
- **Purpose**: Generates realistic lip-synced videos from static images and audio
- **Key Models**:
  - `facevid2vid_00189-model.pth.tar`: Main video generation model
  - `epoch_20.pth`: Core training checkpoint
  - Audio-to-pose and audio-to-expression models for realistic movement
- **Resolution**: Supports both 256px and 512px output
- **License**: Custom license (see SadTalker/LICENSE)

### GFPGAN
- **Purpose**: Face enhancement and restoration
- **Function**: Improves quality of generated faces
- **Optional**: Application works without GFPGAN but with lower quality

### Stable Diffusion
- **Purpose**: Character image generation from text descriptions
- **Model**: Uses Hugging Face's diffusion models
- **Customizable**: Can be configured for different art styles

### Text-to-Speech
- **Purpose**: Converts scripts to natural-sounding audio
- **Engine**: Configurable TTS engine
- **Languages**: Supports multiple languages

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Reduce batch size or use CPU mode
2. **Model Loading Errors**: Ensure all models are downloaded correctly
3. **Import Errors**: Check that all dependencies are installed with Poetry

### Performance Optimization

- Use GPU acceleration when available
- Adjust model resolution based on hardware capabilities
- Monitor memory usage during generation

## Development

### Project Structure

```
digital-human-rag-agent/
├── src/                    # Main application code
│   ├── main.py            # Flask web application
│   ├── llm.py             # Language model interactions
│   ├── image_generator.py # Image generation
│   ├── audio_generator.py # Audio generation
│   └── video_generator.py # Video generation
├── SadTalker/             # SadTalker submodule
├── templates/             # HTML templates
├── static/               # Static web assets
├── prompts/              # LLM prompts
└── docs/                 # Documentation
```

### Adding New Features

1. Follow the modular architecture
2. Add new modules to the `src/` directory
3. Update the main application to integrate new features
4. Add appropriate tests and documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [SadTalker](https://github.com/OpenTalker/SadTalker) for the lip-sync video generation
- [GFPGAN](https://github.com/TencentARC/GFPGAN) for face enhancement
- [Stable Diffusion](https://huggingface.co/stabilityai) for image generation
- [Hugging Face](https://huggingface.co/) for model hosting and APIs

## Model Storage Notice

⚠️ **Important**: Model files are not included in this repository due to their large size (7.6GB total). You must download them separately using the provided script. The models are essential for the application to function properly.

The following directories will be created after running the download script:
- `checkpoints/` - Main model checkpoints
- `gfpgan/` - Face enhancement models  
- `SadTalker/checkpoints/` - SadTalker-specific models
- `SadTalker/gfpgan/` - SadTalker's GFPGAN models

These directories are excluded from version control to keep the repository size manageable. 