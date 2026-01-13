"""
Configuration module for the Finnish Blog Post Generator.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = OUTPUT_DIR / "images"
# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model settings
TEXT_MODEL = "gemini-2.0-flash"
IMAGE_MODEL = "gemini-2.0-flash-exp"

# Finnish level settings
FINNISH_LEVELS = ["A1", "A2"]
DEFAULT_LEVEL = "A1-A2"

# Topic categories for A1-A2 Finnish
TOPIC_CATEGORIES = [
    # Culture & Lifestyle
    "Finnish Culture and Traditions",
    "Travel and Tourism in Finland",
    "Finnish Food and Dining",
    "Nature and Outdoors",
    "Finnish Lifestyle and Society",
    "Sauna Culture",
    "Finnish Design and Arts",
    "Famous Finnish People",
    "Cities and Places to Visit",
    
    # Practical Life
    "Daily Routines in Finland",
    "Shopping and Money",
    "Work and Professions",
    "Hobbies and Free Time",
    "Home and Living",
    "Health and Well-being",
    
    # Language Basics
    "Greetings and Introductions",
    "Numbers and Counting",
    "Family and Relationships",
    "Time and Calendar",
    "Weather and Seasons",
    "Basic Grammar Tips",
    "Common Expressions",
]

# Blog post template settings
BLOG_SETTINGS = {
    "min_words": 800,
    "max_words": 1500,
    "include_vocabulary": True,
    "include_grammar_tips": True,
    "include_exercises": True,
    "include_cultural_notes": True
}
