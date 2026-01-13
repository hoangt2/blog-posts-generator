#!/usr/bin/env python3
"""
Finnish Blog Post Generator - CLI Entry Point

Generate daily MDX blog posts for Finnish language learners using Gemini AI.
"""

import click
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.config import OUTPUT_DIR, IMAGES_DIR

from src.topic_manager import TopicManager
from src.blog_generator import generate_topic_suggestion, generate_blog_post
from src.image_generator import generate_blog_header_image
from src.mdx_formatter import create_mdx_file, preview_post


@click.group()
def cli():
    """Finnish Blog Post Generator - AI-powered content for language learners."""
    pass





@cli.command()
@click.option('--date', '-d', type=str, help='Target date (YYYY-MM-DD). Defaults to next available date.')
@click.option('--topic', '-t', type=str, help='Force a specific topic instead of AI selection.')
@click.option('--days', '-n', type=int, default=1, help='Number of posts to generate (consecutive days).')
@click.option('--level', '-l', type=str, default='A1-A2', help='Finnish level (A1, A2, or A1-A2).')
@click.option('--no-image', is_flag=True, help='Skip image generation.')
@click.option('--dry-run', is_flag=True, help='Preview without saving files.')
def generate(
    date: Optional[str],
    topic: Optional[str],
    days: int,
    level: str,
    no_image: bool,
    dry_run: bool
):
    """Generate one or more blog posts."""
    topic_manager = TopicManager()
    
    # Determine starting date
    if date:
        try:
            start_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            click.echo(f"❌ Invalid date format: {date}. Use YYYY-MM-DD.")
            return
    else:
        # Get next available date
        next_date_str = topic_manager.get_next_available_date()
        start_date = datetime.strptime(next_date_str, '%Y-%m-%d')
    
    click.echo(f"🚀 Generating {days} blog post(s) starting from {start_date.strftime('%Y-%m-%d')}")
    click.echo(f"   Level: {level}")
    click.echo(f"   Image generation: {'❌ Disabled' if no_image else '✅ Enabled'}")
    click.echo(f"   Mode: {'🔍 DRY RUN' if dry_run else '💾 SAVE'}")
    click.echo("")
    
    generated_posts = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Check if date is already used
        if topic_manager.is_date_used(date_str):
            click.echo(f"⚠️  Skipping {date_str} - already has a post")
            continue
        
        click.echo(f"\n{'='*50}")
        click.echo(f"📅 Generating post for {date_str} ({i+1}/{days})")
        click.echo(f"{'='*50}")
        
        # Get topic
        if topic and i == 0:
            # Use provided topic for first post only
            current_topic = topic
            current_category = None
            click.echo(f"📝 Using specified topic: {current_topic}")
        else:
            click.echo("🤖 AI selecting topic...")
            suggestion = generate_topic_suggestion(topic_manager)
            current_topic = suggestion['topic']
            current_category = suggestion.get('category')
            click.echo(f"   Topic: {current_topic}")
            click.echo(f"   Category: {current_category}")
            click.echo(f"   Brief: {suggestion.get('brief', '')[:100]}...")
        
        # Generate blog post
        click.echo("\n✍️  Generating blog content...")
        post_data = generate_blog_post(
            topic=current_topic,
            date=date_str,
            category=current_category,
            level=level
        )
        
        click.echo(f"   Title: {post_data['title']}")
        click.echo(f"   Description: {post_data['description'][:80]}...")
        click.echo(f"   Tags: {', '.join(post_data['tags'][:5])}")
        
        # Generate image
        image_path = None
        if not no_image:
            click.echo("\n🎨 Generating header image...")
            image_prompt = post_data.get('image_prompt', '')
            if image_prompt:
                click.echo(f"   Prompt: {image_prompt[:80]}...")
            
            if not dry_run:
                image_path = generate_blog_header_image(
                    topic=current_topic,
                    date=date_str,
                    custom_prompt=image_prompt
                )
                if image_path:
                    click.echo(f"   ✅ Image saved: {image_path.name}")
                else:
                    click.echo("   ⚠️  Image generation failed, continuing without image")
            else:
                click.echo("   (Skipped in dry run mode)")
        
        # Save or preview
        if dry_run:
            click.echo("\n" + preview_post(post_data))
        else:
            # Create MDX file
            click.echo("\n💾 Saving MDX file...")
            output_path = create_mdx_file(post_data, image_path)
            click.echo(f"   ✅ Saved: {output_path.name}")
            
            # Record topic and date
            topic_manager.record_topic(
                topic=current_topic,
                date=date_str,
                category=current_category,
                metadata={
                    "title": post_data['title'],
                    "level": level,
                    "tags": post_data['tags']
                }
            )
            
            generated_posts.append({
                "date": date_str,
                "title": post_data['title'],
                "file": output_path.name
            })
    
    # Summary
    click.echo(f"\n{'='*50}")
    click.echo("✨ GENERATION COMPLETE")
    click.echo(f"{'='*50}")
    
    if generated_posts:
        click.echo(f"\n📝 Generated {len(generated_posts)} post(s):")
        for post in generated_posts:
            click.echo(f"   • {post['date']}: {post['title']}")
            click.echo(f"     File: {post['file']}")
        
        click.echo(f"\n📁 Output directory: {OUTPUT_DIR}")
    else:
        click.echo("\n(No posts generated in dry run mode)")


@cli.command()
@click.option('--list', '-l', 'list_topics', is_flag=True, help='List all used topics.')
@click.option('--clear', is_flag=True, help='Clear all topic history (use with caution!).')
@click.option('--suggest', '-s', is_flag=True, help='Get an AI topic suggestion.')
def topics(list_topics: bool, clear: bool, suggest: bool):
    """Manage topic history."""
    topic_manager = TopicManager()
    
    if clear:
        if click.confirm('⚠️  Are you sure you want to clear all topic history?'):
            topic_manager.clear_history()
            click.echo("✅ Topic history cleared.")
        return
    
    if suggest:
        click.echo("🤖 Getting AI topic suggestion...")
        suggestion = generate_topic_suggestion(topic_manager)
        click.echo(f"\n📝 Suggested Topic: {suggestion['topic']}")
        click.echo(f"   Category: {suggestion.get('category', 'N/A')}")
        click.echo(f"   Brief: {suggestion.get('brief', 'N/A')}")
        return
    
    if list_topics:
        topics_list = topic_manager.list_all_topics()
        
        if topics_list:
            click.echo(f"\n📚 Topic History ({len(topics_list)} topics):")
            click.echo("-" * 50)
            
            for t in topics_list:
                click.echo(f"  📅 {t.get('date', 'N/A')}: {t['topic']}")
                if t.get('category'):
                    click.echo(f"     Category: {t['category']}")
            
            click.echo("-" * 50)
        else:
            click.echo("\n📭 No topics recorded yet.")
        
        # Show available categories
        available = topic_manager.get_available_categories()
        click.echo(f"\n🎯 Unexplored categories ({len(available)}):")
        for cat in available[:10]:
            click.echo(f"   • {cat}")
        if len(available) > 10:
            click.echo(f"   ... and {len(available) - 10} more")
        
        return
    
    # Default: show summary
    used = topic_manager.get_used_topics()
    available = topic_manager.get_available_categories()
    
    click.echo(f"\n📊 Topic Summary:")
    click.echo(f"   Used topics: {len(used)}")
    click.echo(f"   Available categories: {len(available)}")
    click.echo(f"\nUse --list to see all topics, or --suggest for AI recommendation.")


@cli.command()
def status():
    """Show generator status and statistics."""
    topic_manager = TopicManager()
    
    click.echo("\n📊 Blog Post Generator Status")
    click.echo("=" * 40)
    
    # Count existing posts
    mdx_files = list(OUTPUT_DIR.glob("*.mdx"))
    image_files = list(IMAGES_DIR.glob("*.png"))
    
    click.echo(f"\n📝 Generated Posts: {len(mdx_files)}")
    click.echo(f"🖼️  Generated Images: {len(image_files)}")
    
    # Topic stats
    used_topics = topic_manager.get_used_topics()
    available = topic_manager.get_available_categories()
    
    click.echo(f"\n📚 Topics:")
    click.echo(f"   Used: {len(used_topics)}")
    click.echo(f"   Available categories: {len(available)}")
    
    # Next available date
    next_date = topic_manager.get_next_available_date()
    click.echo(f"\n📅 Next available date: {next_date}")
    
    # Recent posts
    if mdx_files:
        recent = sorted(mdx_files, reverse=True)[:5]
        click.echo(f"\n📄 Recent posts:")
        for f in recent:
            click.echo(f"   • {f.name}")


if __name__ == "__main__":
    cli()
