"""
AI Image Generator for blog post illustrations.
Uses Gemini's image generation capabilities.
"""

import base64
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types
from PIL import Image
import io
import re

from .config import GEMINI_API_KEY, IMAGE_MODEL, IMAGES_DIR


def get_client():
    """Get the Gemini client."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_image(
    prompt: str,
    filename: str,
    style: str = "modern flat illustration"
) -> Optional[Path]:
    """
    Generate an image using Gemini AI.
    
    Args:
        prompt: Description of the image to generate
        filename: Name for the output file (without extension)
        style: Art style to apply
    
    Returns:
        Path to the saved image, or None if generation failed
    """
    client = get_client()
    
    # Enhanced prompt for better results
    full_prompt = f"""Create a {style} for a Finnish language learning blog.

Image description: {prompt}

Requirements:
- Clean, professional design suitable for educational content
- Warm, inviting colors (consider Finnish nature: blues, greens, whites)
- No text in the image (text will be added separately)
- Simple composition that works well as a blog header
- Modern, minimalist aesthetic
"""
    
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["image", "text"]
            )
        )
        
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                
                # Save the image
                output_path = IMAGES_DIR / f"{filename}.png"
                
                # Decode and save
                image = Image.open(io.BytesIO(image_data))
                image.save(output_path, "PNG")
                
                print(f"Image saved to: {output_path}")
                return output_path
        
        print("No image data in response")
        return None
        
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None


def generate_blog_header_image(
    topic: str,
    date: str,
    custom_prompt: Optional[str] = None
) -> Optional[Path]:
    """
    Generate a header image for a blog post.
    
    Args:
        topic: The blog post topic
        date: The post date (used for filename)
        custom_prompt: Optional custom image description
    
    Returns:
        Path to the generated image
    """
    if custom_prompt:
        prompt = custom_prompt
    else:
        # Generate a default prompt based on topic
        prompt = f"""A warm, inviting illustration representing "{topic}" 
        for Finnish language learners. The scene should evoke Finland's 
        culture and lifestyle while being educational and approachable."""
    
    # Create filename from date and topic
    slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:30]
    filename = f"{date}-{slug}"
    
    return generate_image(prompt, filename)


def generate_vocabulary_card_image(
    finnish_word: str,
    english_translation: str,
    date: str
) -> Optional[Path]:
    """
    Generate a vocabulary flashcard-style image.
    
    Args:
        finnish_word: The Finnish word
        english_translation: English translation
        date: Date for filename uniqueness
    
    Returns:
        Path to the generated image
    """
    prompt = f"""A simple, clean illustration representing the Finnish word "{finnish_word}" 
    (meaning "{english_translation}" in English). 
    The image should be iconic and memorable, helping learners associate 
    the visual with the word. No text should be in the image."""
    
    filename = f"{date}-vocab-{finnish_word.lower()}"
    
    return generate_image(prompt, filename, style="simple icon illustration")


if __name__ == "__main__":
    # Test image generation
    print("Testing image generation...")
    
    result = generate_blog_header_image(
        topic="Finnish Greetings",
        date="2026-01-14",
        custom_prompt="A friendly illustration showing people greeting each other in Finland, with a cozy café in the background during winter"
    )
    
    if result:
        print(f"Success! Image saved to: {result}")
    else:
        print("Image generation failed")
