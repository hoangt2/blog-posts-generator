"""
MDX Formatter for blog posts.
Formats generated content into SEO-friendly MDX files.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config import OUTPUT_DIR


def create_schema_markup(
    title: str,
    date: str,
    description: str,
    image_url: str = "",
    author: str = "Kielo Finnish"
) -> str:
    """
    Create JSON-LD Article schema markup for SEO.
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": date,
        "dateModified": date,
        "author": {
            "@type": "Person",
            "name": author
        },
        "publisher": {
            "@type": "Organization",
            "name": "Kielo",
            "logo": {
                "@type": "ImageObject",
                "url": "https://kielo.io/logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage"
        }
    }
    
    if image_url:
        schema["image"] = image_url
    
    # Return as single-line JSON string for frontmatter (avoids MDX parsing issues)
    return json.dumps(schema)


def create_frontmatter(
    title: str,
    date: str,
    description: str,
    tags: List[str],
    level: str,
    category: str,
    image_path: Optional[str] = None,
    slug: Optional[str] = None,
    schema_json: Optional[str] = None
) -> str:
    """
    Create YAML frontmatter for the MDX file.
    Schema is included as a JSON string field that can be injected in <head> by Next.js.
    """
    # Format tags for YAML
    tags_yaml = "\n".join(f'  - "{tag}"' for tag in tags)
    
    # Image path for the blog (relative URL)
    if image_path:
        image_url = f"/images/{Path(image_path).name}"
    else:
        image_url = ""
    
    # For YAML: use single quotes for fields that may contain double quotes
    # Escape any single quotes in the content by doubling them (YAML standard)
    title_safe = title.replace("'", "''")
    description_safe = description.replace("'", "''")
    
    # Escape quotes in schema_json for YAML
    schema_line = ""
    if schema_json:
        # Single-line JSON string in frontmatter
        schema_line = f'\nschemaMarkup: \'{schema_json}\''
    
    frontmatter = f"""---
title: '{title_safe}'
date: "{date}"
description: '{description_safe}'
slug: "{slug or create_slug(title)}"
level: "{level}"
category: "{category}"
tags:
{tags_yaml}
image: "{image_url}"
author: "Kielo Finnish"
draft: false{schema_line}
---"""
    
    return frontmatter


def create_slug(title: str) -> str:
    """Create a URL-friendly slug from a title."""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def add_mdx_components(content: str) -> str:
    """
    Enhance content with MDX components and formatting.
    Add callouts, tips, and other interactive elements.
    """
    enhanced = content
    
    # Convert markdown blockquotes with special prefixes to callouts
    # > 💡 Tip: ... -> <Callout type="tip">...</Callout>
    enhanced = re.sub(
        r'^>\s*💡\s*(?:Tip|Vinkki):\s*(.+?)$',
        r'<Callout type="tip">\n\1\n</Callout>',
        enhanced,
        flags=re.MULTILINE
    )
    
    # > ⚠️ Note: ... -> <Callout type="warning">...</Callout>
    enhanced = re.sub(
        r'^>\s*⚠️\s*(?:Note|Huom):\s*(.+?)$',
        r'<Callout type="warning">\n\1\n</Callout>',
        enhanced,
        flags=re.MULTILINE
    )
    
    # > 🇫🇮 Cultural Note: ... -> <Callout type="info">...</Callout>
    enhanced = re.sub(
        r'^>\s*🇫🇮\s*(?:Cultural Note|Kulttuurivinkki):\s*(.+?)$',
        r'<Callout type="info" title="Cultural Note">\n\1\n</Callout>',
        enhanced,
        flags=re.MULTILINE
    )
    
    # Wrap vocabulary tables nicely
    # This assumes vocabulary is in a table format
    
    return enhanced


def format_vocabulary_section(vocabulary: List[Dict]) -> str:
    """
    Format vocabulary into a nice table.
    
    Args:
        vocabulary: List of dicts with keys: finnish, english, example, example_translation
    """
    if not vocabulary:
        return ""
    
    lines = [
        "## 📚 Vocabulary / Sanasto",
        "",
        "| Finnish | English | Example |",
        "|---------|---------|---------|"
    ]
    
    for word in vocabulary:
        finnish = word.get('finnish', '')
        english = word.get('english', '')
        example = word.get('example', '')
        lines.append(f"| **{finnish}** | {english} | *{example}* |")
    
    return "\n".join(lines)


def create_mdx_file(
    post_data: Dict,
    image_path: Optional[Path] = None
) -> Path:
    """
    Create a complete MDX file from blog post data.
    
    Args:
        post_data: Dict containing title, content, description, tags, etc.
        image_path: Optional path to the generated image
    
    Returns:
        Path to the created MDX file
    """
    title = post_data.get('title', 'Untitled')
    date = post_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    description = post_data.get('description', '')
    tags = post_data.get('tags', ['finnish', 'language-learning'])
    level = post_data.get('level', 'A1-A2')
    category = post_data.get('category', 'General')
    slug = post_data.get('slug', create_slug(title))
    content = post_data.get('content', '')
    image_alt = post_data.get('image_alt', f'Illustration for {title}')
    
    # Determine image URL for schema
    image_url = ""
    if image_path:
        image_name = Path(image_path).name
        image_url = f"/images/{image_name}"
    
    # Create JSON-LD schema markup for SEO (goes in frontmatter)
    schema_json = create_schema_markup(
        title=title,
        date=date,
        description=description,
        image_url=image_url
    )
    
    # Create frontmatter (includes schema as JSON string field)
    frontmatter = create_frontmatter(
        title=title,
        date=date,
        description=description,
        tags=tags,
        level=level,
        category=category,
        image_path=str(image_path) if image_path else None,
        slug=slug,
        schema_json=schema_json
    )
    
    # Add image to content if available (with proper alt text)
    content_with_image = content
    if image_path:
        # Use descriptive alt text for SEO (max 125 chars)
        alt_text = image_alt[:125] if len(image_alt) > 125 else image_alt
        content_with_image = f"![{alt_text}]({image_url})\n\n{content}"
    
    # Enhance with MDX components
    enhanced_content = add_mdx_components(content_with_image)
    
    # Combine: frontmatter + content (no script in body - schema is in frontmatter)
    full_content = f"{frontmatter}\n\n{enhanced_content}"
    
    # Create output file
    filename = f"{date}-{slug}.mdx"
    output_path = OUTPUT_DIR / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"Created: {output_path}")
    return output_path


def preview_post(post_data: Dict) -> str:
    """
    Generate a preview of the post without saving.
    Useful for dry runs.
    """
    title = post_data.get('title', 'Untitled')
    date = post_data.get('date', 'TBD')
    description = post_data.get('description', '')
    tags = post_data.get('tags', [])
    content = post_data.get('content', '')
    
    preview = f"""
{'='*60}
BLOG POST PREVIEW
{'='*60}

Title: {title}
Date: {date}
Description: {description}
Tags: {', '.join(tags)}

{'='*60}
CONTENT PREVIEW (first 500 chars):
{'='*60}

{content[:500]}...

{'='*60}
"""
    return preview


if __name__ == "__main__":
    # Test MDX formatting
    test_data = {
        "title": "Learn Finnish Greetings: Moi, Hei, and More!",
        "date": "2026-01-14",
        "description": "Master essential Finnish greetings for everyday conversations.",
        "tags": ["finnish", "greetings", "A1", "beginner", "vocabulary"],
        "level": "A1",
        "category": "Vocabulary",
        "slug": "finnish-greetings-moi-hei",
        "content": """# Welcome to Finnish Greetings!

Learning how to greet people is the first step in any language journey.

## Common Greetings

| Finnish | English |
|---------|---------|
| Moi | Hi (informal) |
| Hei | Hello |
| Terve | Hello/Hi |
| Huomenta | Good morning |

> 💡 Tip: "Moi moi" is commonly used when saying goodbye!

> 🇫🇮 Cultural Note: Finns appreciate direct greetings without too much small talk.
"""
    }
    
    print(preview_post(test_data))
