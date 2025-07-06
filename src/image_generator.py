from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
import torch
from pathlib import Path
import numpy as np
import os

from . import config

def generate_avatar_image(image_prompt: str) -> Path:
    """
    Generates an avatar image using a Stable Diffusion model optimized for Apple Silicon MPS.

    Args:
        image_prompt (str): The prompt to generate the avatar image.

    Returns:
        Path: The path to the generated avatar image.
    """
    print("Generating avatar image...")
    
    # Enable MPS fallback for unsupported operations
    os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
    
    # Determine optimal settings for MPS
    use_mps = config.DEVICE == "mps"
    
    if use_mps:
        # For MPS, use float32 to avoid precision issues
        torch_dtype = torch.float32
        variant = None  # Don't use fp16 variant on MPS
        print("Using MPS device with float32 precision for stability")
    else:
        # For other devices, use the configured dtype
        torch_dtype = torch.float16 if config.TORCH_DTYPE == "auto" else config.TORCH_DTYPE
        variant = "fp16" if torch_dtype == torch.float16 else None
    
    # Load the pipeline with MPS-optimized settings
    pipe = DiffusionPipeline.from_pretrained(
        config.IMAGE_MODEL_ID,
        torch_dtype=torch_dtype,
        use_safetensors=True,
        variant=variant,
        cache_dir=str(config.CACHE_DIR)
    )
    
    # Use a more MPS-friendly scheduler
    if use_mps:
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    pipe = pipe.to(config.DEVICE)
    
    # Apply MPS-specific optimizations
    if use_mps:
        # Enable attention slicing for memory efficiency (recommended for MPS)
        pipe.enable_attention_slicing()
        
        # Enable memory efficient attention if available
        try:
            pipe.enable_xformers_memory_efficient_attention()
            print("Enabled xformers memory efficient attention")
        except Exception:
            print("xformers not available, using standard attention")
        
        # Set scheduler to use float32 for numerical stability
        if hasattr(pipe.scheduler, 'set_timesteps'):
            original_set_timesteps = pipe.scheduler.set_timesteps
            def set_timesteps_mps(*args, **kwargs):
                # Ensure timesteps are in float32 for MPS stability
                result = original_set_timesteps(*args, **kwargs)
                if hasattr(pipe.scheduler, 'timesteps'):
                    pipe.scheduler.timesteps = pipe.scheduler.timesteps.to(torch.float32)
                return result
            pipe.scheduler.set_timesteps = set_timesteps_mps

    # Generate the image with error handling
    try:
        # Use optimized settings for MPS
        generation_kwargs = {
            "num_inference_steps": 20,  # Fewer steps for faster generation
            "guidance_scale": 7.5
        }
        
        if use_mps:
            # Additional MPS optimizations
            generation_kwargs.update({
                "num_inference_steps": 15,  # Even fewer steps on MPS for speed
                "guidance_scale": 7.0,  # Slightly lower guidance for stability
                "output_type": "pil"  # Ensure PIL output for CPU compatibility
            })
        
        image = pipe(image_prompt, **generation_kwargs).images[0]
        
        # Validate the generated image
        img_array = np.array(image)
        if img_array.max() == 0 or np.isnan(img_array).any():
            raise ValueError("Generated image is invalid (all zeros or contains NaN)")
        
        print(f"Successfully generated image on {config.DEVICE}")
            
    except Exception as e:
        print(f"MPS generation failed: {e}")
        
        if use_mps:
            print("Falling back to CPU with optimized settings...")
            # Reload pipeline for CPU with proper settings
            pipe = DiffusionPipeline.from_pretrained(
                config.IMAGE_MODEL_ID,
                torch_dtype=torch.float32,  # Use float32 for CPU
                use_safetensors=True,
                variant="fp16", # Load the cached fp16 files but Pytorch will use fp32
                cache_dir=str(config.CACHE_DIR)
            )
            pipe = pipe.to("cpu")
            
            # Generate on CPU
            image = pipe(
                image_prompt,
                num_inference_steps=20,
                guidance_scale=7.5
            ).images[0]
            
            print("Successfully generated image on CPU fallback")
        else:
            raise e
    
    # Ensure the destination directory exists
    image_path = config.GENERATED_IMAGE_PATH
    image_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the image
    image.save(image_path)
    print(f"Avatar image saved to {image_path}")
    
    # Clean up GPU memory if using MPS
    if use_mps:
        torch.mps.empty_cache()
    
    return image_path

if __name__ == '__main__':
    # Example usage
    prompt = "A realistic photo of a male European, wearing glasses and a leather jacket with a smile on his face, front view, neutral expression, simple background"
    generate_avatar_image(prompt) 