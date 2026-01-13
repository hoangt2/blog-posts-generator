"""
Topic Manager for Finnish Blog Post Generator.
Tracks used topics and dates to ensure variety and no duplicates.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from .config import DATA_DIR, TOPIC_CATEGORIES


class TopicManager:
    """Manages topic selection and tracking for blog posts."""
    
    def __init__(self):
        self.topics_file = DATA_DIR / "topics_history.json"
        self.dates_file = DATA_DIR / "dates_used.json"
        self._load_data()
    
    def _load_data(self):
        """Load existing topic and date history."""
        # Load topics history
        if self.topics_file.exists():
            with open(self.topics_file, 'r', encoding='utf-8') as f:
                self.topics_history = json.load(f)
        else:
            self.topics_history = {
                "used_topics": [],
                "topic_details": {}
            }
        
        # Load dates used
        if self.dates_file.exists():
            with open(self.dates_file, 'r', encoding='utf-8') as f:
                self.dates_used = json.load(f)
        else:
            self.dates_used = {"dates": []}
    
    def _save_data(self):
        """Save topic and date history."""
        with open(self.topics_file, 'w', encoding='utf-8') as f:
            json.dump(self.topics_history, f, ensure_ascii=False, indent=2)
        
        with open(self.dates_file, 'w', encoding='utf-8') as f:
            json.dump(self.dates_used, f, ensure_ascii=False, indent=2)
    
    def get_used_topics(self) -> List[str]:
        """Get list of already used topics."""
        return self.topics_history.get("used_topics", [])
    
    def get_available_categories(self) -> List[str]:
        """Get topic categories that haven't been fully explored."""
        used = set(self.get_used_topics())
        return [cat for cat in TOPIC_CATEGORIES if cat not in used]
    
    def is_date_used(self, date: str) -> bool:
        """Check if a date has already been used."""
        return date in self.dates_used.get("dates", [])
    
    def get_next_available_date(self, start_date: Optional[datetime] = None) -> str:
        """Get the next available date that hasn't been used."""
        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)
        
        current = start_date
        max_attempts = 365  # Don't loop forever
        
        for _ in range(max_attempts):
            date_str = current.strftime("%Y-%m-%d")
            if not self.is_date_used(date_str):
                return date_str
            current += timedelta(days=1)
        
        raise ValueError("No available dates found in the next year")
    
    def get_context_for_ai(self) -> str:
        """
        Get context about used topics for AI to make informed decisions.
        """
        used_topics = self.get_used_topics()
        available_categories = self.get_available_categories()
        
        context_parts = [
            "## Topic History",
            f"Previously covered topics ({len(used_topics)} total):",
        ]
        
        if used_topics:
            for topic in used_topics[-10:]:  # Last 10 topics
                context_parts.append(f"  - {topic}")
            if len(used_topics) > 10:
                context_parts.append(f"  ... and {len(used_topics) - 10} more")
        else:
            context_parts.append("  (No topics used yet)")
        
        context_parts.append(f"\nAvailable categories to explore:")
        for cat in available_categories[:10]:
            context_parts.append(f"  - {cat}")
        
        return "\n".join(context_parts)
    
    def record_topic(
        self,
        topic: str,
        date: str,
        category: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Record a topic as used.
        
        Args:
            topic: The specific topic title
            date: The date the topic was used (YYYY-MM-DD)
            category: The broader category (optional)
            metadata: Additional info like keywords, level, etc.
        """
        # Add to used topics
        if topic not in self.topics_history["used_topics"]:
            self.topics_history["used_topics"].append(topic)
        
        # Store details
        self.topics_history["topic_details"][topic] = {
            "date": date,
            "category": category,
            "metadata": metadata or {},
            "recorded_at": datetime.now().isoformat()
        }
        
        # Record date
        if date not in self.dates_used["dates"]:
            self.dates_used["dates"].append(date)
            self.dates_used["dates"].sort()
        
        self._save_data()
    
    def suggest_topic_prompt(self) -> str:
        """
        Generate a prompt section for AI to select a new topic.
        """
        context = self.get_context_for_ai()
        available = self.get_available_categories()
        
        prompt = f"""
{context}

Based on this history, suggest a NEW topic for a Finnish language learning blog post.

Requirements:
- Target level: A1-A2 (beginner)
- Must be different from previously covered topics
- Should be practical and useful for daily life
- Consider these unexplored categories: {', '.join(available[:5])}

Provide your topic suggestion in this format:
TOPIC: [Your topic title]
CATEGORY: [Matching category from the list]
BRIEF: [2-3 sentence description of what the post will cover]
"""
        return prompt
    
    def list_all_topics(self) -> List[Dict]:
        """Get all recorded topics with their details."""
        result = []
        for topic in self.topics_history.get("used_topics", []):
            details = self.topics_history.get("topic_details", {}).get(topic, {})
            result.append({
                "topic": topic,
                "date": details.get("date"),
                "category": details.get("category"),
                "metadata": details.get("metadata", {})
            })
        return result
    
    def clear_history(self):
        """Clear all topic and date history. Use with caution!"""
        self.topics_history = {"used_topics": [], "topic_details": {}}
        self.dates_used = {"dates": []}
        self._save_data()


if __name__ == "__main__":
    # Test topic manager
    tm = TopicManager()
    print("Used topics:", tm.get_used_topics())
    print("\nAvailable categories:", tm.get_available_categories())
    print("\nNext available date:", tm.get_next_available_date())
    print("\nAI context:")
    print(tm.get_context_for_ai())
