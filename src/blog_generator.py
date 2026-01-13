"""
Blog Post Generator using Gemini AI.
Generates engaging Finnish language learning content.
"""

from google import genai
from google.genai import types
from typing import Dict, List, Optional
import re

from .config import GEMINI_API_KEY, TEXT_MODEL, BLOG_SETTINGS, DEFAULT_LEVEL
from .topic_manager import TopicManager


def get_client():
    """Get the Gemini client."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    return genai.Client(api_key=GEMINI_API_KEY)





def generate_topic_suggestion(topic_manager: TopicManager) -> Dict[str, str]:
    """
    Use AI to suggest a new topic based on history and available content.
    
    Returns dict with: topic, category, brief
    """
    client = get_client()
    
    prompt = f"""You are a creative Finnish culture & lifestyle editor planning blog topics.

{topic_manager.suggest_topic_prompt()}

SUGGEST A NEW TOPIC from categories like:
- Finnish Culture & Traditions
- Travel & Tourism
- Food & Dining
- Lifestyle & Society
- Nature & Outdoors

The topic should be engaging, like a magazine article title (e.g. "Why Finns Love Sauna", "Top 5 Foods to Try", "Lapland Northern Lights Guide").
AVOID purely grammatical titles like "The Genitive Case".

Remember to output in this exact format:
TOPIC: [topic title - specific and catchy]
CATEGORY: [category name]
BRIEF: [2-3 sentence description of the cultural angle]
"""
    
    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt
    )
    text = response.text
    
    # Parse the response
    topic_match = re.search(r'TOPIC:\s*(.+?)(?:\n|$)', text)
    category_match = re.search(r'CATEGORY:\s*(.+?)(?:\n|$)', text)
    brief_match = re.search(r'BRIEF:\s*(.+?)(?:\n|$)', text, re.DOTALL)
    
    return {
        "topic": topic_match.group(1).strip() if topic_match else "Finnish Basics",
        "category": category_match.group(1).strip() if category_match else "General",
        "brief": brief_match.group(1).strip() if brief_match else ""
    }


def generate_blog_post(
    topic: str,
    date: str,
    category: Optional[str] = None,
    level: str = DEFAULT_LEVEL,
    custom_context: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate a complete blog post using Gemini AI.
    
    Args:
        topic: The topic to write about
        date: Publication date (YYYY-MM-DD)
        category: Topic category
        level: Finnish level (A1, A2, or A1-A2)
        custom_context: Optional additional context
    
    Returns:
        Dict with: title, content, description, tags, slug, image_prompt
    """
    client = get_client()
    
    settings = BLOG_SETTINGS
    
    prompt = f"""You are an expert Finnish culture and language guide creating an engaging blog post for people interested in Finland.

## Topic Information
- Topic: {topic}
- Primary Keyword: "{topic}" (use this exact phrase strategically)
- Category: {category or 'Finnish Culture'}
- Target Audience: People interested in Finland, culture, travel, and lifestyle (plus language learners)
- Target Level: {level} (for the language lesson part)
- Publication Date: {date}

{f"## Additional Context: {custom_context}" if custom_context else ""}

## Blog Post Requirements

Create an engaging, magazine-style blog post that focuses on **Finnish culture, lifestyle, people, or tourism**. The main content should be in English and very readable. Include a dedicated "Language Corner" for a small lesson.

### 1. TITLE TAG (Critical for SEO)
- **Maximum 60 characters** (strict!)
- Include the primary keyword near the BEGINNING
- Make it inviting and descriptive
- Example: "Finnish Sauna Culture: A Beginner's Guide"

### 2. META DESCRIPTION
- **~105 characters** (max 120)
- Active voice, inviting, ends with CTA
- Example: "Discover the magic of Finnish sauna culture. Read our guide now!"

### 3. URL SLUG
- 3-5 words, keyword-rich, hyphens

### 4. CONTENT STRUCTURE (Use proper Markdown headings!)
Write {settings['min_words']}-{settings['max_words']} words using this EXACT structure:

```
# [Main Title]

[Engaging Hook Paragraph about the topic]

## [Engaging Subheading about the Cultural Aspect]
[Main content: Discuss the topic deep diving into Finnish culture, lifestyle, history, or travel tips.
Make this the bulk of the post (70%). Write in clear, engaging English.
Share interesting facts, local insights, and "hidden gems".
If it's about food, describe the taste/tradition. If travel, describe the experience.]

## [Another Cultural Subheading]
[Continue the cultural exploration. Use specific examples, anecdotes, or advice.]

## 🇫🇮 Language Corner / Kielinurkka
[This is the "mini lesson" (30%). Teach specific vocabulary or phrases RELATED to the main topic above.]

### Useful Phrases
[3-5 key phrases related to the topic]
- *Phrase in Finnish* - English translation
- *Phrase in Finnish* - English translation

### Vocabulary / Sanasto
[A small table of 5-8 relevant words]

| Finnish | English | Example |
|---------|---------|---------|
| word | translation | *Example sentence* |

## Cultural Insight
[A "did you know" style fact or pro-tip related to the topic]

## Conclusion
[Wrap up the cultural journey and encourage them to visit/try it]

## References
- [Source Name](URL)
- [Source Name](URL)
```

### 5. SEO CONTENT RULES
- Include primary keyword in: H1, first paragraph, meaningful subheadings
- Use **proper H2/H3 headings**
- **MANDATORY**: Include 2-3 real, functioning links to authoritative sources (YLE, Visit Finland, etc.) within the text or in a "References" section.
- Add "Related Topics" section

### 6. TAGS
- 5-7 tags: topic, "Finnish Culture", "Visit Finland", specific category

### 7. IMAGE PROMPT
- Warm, inviting, high-quality photography style illustration
- Show the **cultural** aspect (e.g. sauna, food, landscape), not just text or classroom
- "No text in image"

## Output Format

Provide your response in this EXACT format:

---TITLE---
[Max 60 chars title]

---SLUG---
[slug-here]

---DESCRIPTION---
[~105 chars meta description]

---TAGS---
[tag1, tag2, tag3]

---IMAGE_PROMPT---
[Visual description of cultural scene]

---IMAGE_ALT---
[Alt text with keyword]

---CONTENT---
[Full blog post with ## headings]

---END---
"""

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    text = response.text
    
    # Parse the response
    def extract_section(text: str, section: str) -> str:
        pattern = rf'---{section}---\s*(.*?)(?=---[A-Z_]+---|---END---|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    title = extract_section(text, "TITLE")
    slug = extract_section(text, "SLUG")
    description = extract_section(text, "DESCRIPTION")
    tags_raw = extract_section(text, "TAGS")
    image_prompt = extract_section(text, "IMAGE_PROMPT")
    image_alt = extract_section(text, "IMAGE_ALT")
    content = extract_section(text, "CONTENT")
    
    # Parse tags
    tags = [tag.strip().strip('"\'') for tag in tags_raw.split(',') if tag.strip()]
    
    # Clean up slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
    
    # Default image alt if not provided
    if not image_alt:
        image_alt = f"Illustration for learning {topic} in Finnish"
    
    return {
        "title": title or topic,
        "slug": slug,
        "description": description,
        "tags": tags,
        "image_prompt": image_prompt,
        "image_alt": image_alt,
        "content": content,
        "level": level,
        "category": category,
        "date": date
    }


if __name__ == "__main__":
    # Test blog generation
    from .topic_manager import TopicManager
    
    tm = TopicManager()
    
    print("Suggesting topic...")
    suggestion = generate_topic_suggestion(tm)
    print(f"Topic: {suggestion['topic']}")
    print(f"Category: {suggestion['category']}")
    print(f"Brief: {suggestion['brief']}")
    
    print("\nGenerating blog post...")
    post = generate_blog_post(
        topic=suggestion['topic'],
        date="2026-01-14",
        category=suggestion['category']
    )
    
    print(f"\nTitle: {post['title']}")
    print(f"Description: {post['description']}")
    print(f"Tags: {post['tags']}")
    print(f"\nContent preview:\n{post['content'][:500]}...")
