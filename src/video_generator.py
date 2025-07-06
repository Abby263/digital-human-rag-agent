import subprocess
import os
from pathlib import Path
import glob

from . import config

def create_ai_influencer_video(image_path: Path, audio_path: Path) -> Path:
    """
    Creates an AI influencer video by animating a source image with an audio file.

    Args:
        image_path (Path): Path to the source image.
        audio_path (Path): Path to the driven audio.

    Returns:
        Path: The path to the generated video file.
    """
    print("Generating lip-synced video...")

    # Convert to absolute paths for SadTalker compatibility
    image_path = image_path.resolve()
    audio_path = audio_path.resolve()
    
    # Verify input files exist
    if not image_path.exists():
        raise FileNotFoundError(f"Source image not found: {image_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    audio_duration_seconds = 0.0
    # Get audio duration to estimate processing time
    try:
        duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)
        ]
        duration_str = subprocess.check_output(duration_cmd).strip().decode('utf-8')
        audio_duration_seconds = float(duration_str)
        # SadTalker tends to take about 2-3x the audio duration, plus some overhead.
        # This provides a rough, conservative estimate.
        estimated_minutes = (audio_duration_seconds * 3 + 30) / 60 
        print(f"Audio duration: {audio_duration_seconds:.2f} seconds. Estimated generation time: ~{estimated_minutes:.1f} minutes.")
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        print(f"Could not determine audio duration: {e}. Continuing without time estimate.")

    print(f"Using image: {image_path}")
    print(f"Using audio: {audio_path}")

    # Ensure result directory is clean before generation
    for f in glob.glob(str(config.RESULT_DIR / '*.mp4')):
        os.remove(f)

    # Use the current Python executable
    import sys
    python_executable = sys.executable
    
    command = [
        str(python_executable), str(config.SADTALKER_INFERENCE_SCRIPT),
        '--driven_audio', str(audio_path),
        '--source_image', str(image_path),
        '--result_dir', str(config.RESULT_DIR.resolve()),
        '--still',
        '--preprocess', 'full'
    ]

    print(f"Running SadTalker command...")
    print(f"This may take a while. For a {audio_duration_seconds:.2f}-second audio, it can take several minutes.")

    # Set up environment with proper Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{config.SADTALKER_DIR}:{env.get('PYTHONPATH', '')}"

    # Run from SadTalker directory for relative imports
    process = subprocess.run(
        command,
        cwd=str(config.SADTALKER_DIR),
        capture_output=True,
        text=True,
        env=env
    )

    if process.returncode != 0:
        print("Error running SadTalker:")
        print("STDOUT:", process.stdout)
        print("STDERR:", process.stderr)
        raise RuntimeError("SadTalker video generation failed.")

    # Find the generated video file
    results = sorted(glob.glob(str(config.RESULT_DIR / '*.mp4')))
    if not results:
        raise FileNotFoundError("SadTalker did not produce a video file.")
    
    generated_video_path = Path(results[0])
    final_video_path = config.GENERATED_VIDEO_PATH
    
    # Ensure the destination directory exists
    final_video_path.parent.mkdir(parents=True, exist_ok=True)

    # Move video to a predictable location
    os.rename(generated_video_path, final_video_path)
    
    print(f"Lip-synced video saved to {final_video_path}")
    return final_video_path

if __name__ == '__main__':
    # Example usage (assumes files exist)
    img_path = config.GENERATED_IMAGE_PATH
    aud_path = config.GENERATED_AUDIO_PATH

    if not img_path.exists() or not aud_path.exists():
        print("Please generate image and audio files first.")
    else:
        create_ai_influencer_video(img_path, aud_path) 