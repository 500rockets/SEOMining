#!/usr/bin/env python
"""
Manual Content Input Tool
Allows you to manually add competitor content when scraping fails
"""
import sys
sys.path.insert(0, '/app')

import json
from app.services.optimization import get_manual_content_manager


def add_manual_content():
    """
    Interactive tool to add manual content for failed scrapes
    """
    print("=" * 80)
    print("  MANUAL CONTENT INPUT TOOL")
    print("  Add competitor content when scraping fails")
    print("=" * 80)
    print()
    
    manager = get_manual_content_manager()
    
    # Show existing content
    existing_content = manager.list_manual_content()
    if existing_content:
        print("Existing manual content:")
        for i, content in enumerate(existing_content, 1):
            print(f"  {i}. {content['url']} ({content['word_count']} words)")
        print()
    
    # Get content from user
    print("Enter competitor content manually:")
    print()
    
    url = input("URL: ").strip()
    if not url:
        print("No URL provided, exiting.")
        return
    
    title = input("Page Title: ").strip()
    if not title:
        title = "No title provided"
    
    print()
    print("Enter the full page content (paste it here, press Ctrl+D when done):")
    print("(You can copy-paste from the actual webpage)")
    print()
    
    content_lines = []
    try:
        while True:
            line = input()
            content_lines.append(line)
    except EOFError:
        pass
    
    content = '\n'.join(content_lines)
    
    if not content.strip():
        print("No content provided, exiting.")
        return
    
    meta_description = input("Meta Description (optional): ").strip()
    
    # Save the content
    filepath = manager.save_manual_content(
        url=url,
        title=title,
        content=content,
        meta_description=meta_description,
        source="manual"
    )
    
    print()
    print("=" * 80)
    print("  CONTENT SAVED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print(f"URL: {url}")
    print(f"Title: {title}")
    print(f"Content Length: {len(content)} characters")
    print(f"Word Count: {len(content.split())} words")
    print(f"Saved to: {filepath}")
    print()
    print("This content will now be used in GPU analysis instead of scraping.")
    print("Run the GPU analysis again to include this content.")


def list_manual_content():
    """List all manually saved content"""
    manager = get_manual_content_manager()
    content_list = manager.list_manual_content()
    
    print("=" * 80)
    print("  MANUAL CONTENT LIBRARY")
    print("=" * 80)
    print()
    
    if not content_list:
        print("No manual content saved yet.")
        print("Use 'add' command to add content manually.")
        return
    
    for i, content in enumerate(content_list, 1):
        print(f"{i}. {content['url']}")
        print(f"   Title: {content['title']}")
        print(f"   Content: {content['content_length']} chars, {content['word_count']} words")
        print(f"   Added: {content['added_at']}")
        print(f"   Source: {content['source']}")
        print()


def show_content_preview():
    """Show preview of manual content"""
    manager = get_manual_content_manager()
    content_list = manager.list_manual_content()
    
    if not content_list:
        print("No manual content available.")
        return
    
    print("Select content to preview:")
    for i, content in enumerate(content_list, 1):
        print(f"{i}. {content['url']}")
    
    try:
        choice = int(input("\nEnter number: ")) - 1
        if 0 <= choice < len(content_list):
            content = content_list[choice]
            print(f"\nContent preview for {content['url']}:")
            print("-" * 80)
            preview = content['content'][:1000] + "..." if len(content['content']) > 1000 else content['content']
            print(preview)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "add":
            add_manual_content()
        elif command == "list":
            list_manual_content()
        elif command == "preview":
            show_content_preview()
        else:
            print("Usage: python manual_content.py [add|list|preview]")
    else:
        print("Manual Content Management Tool")
        print("Usage: python manual_content.py [add|list|preview]")
        print()
        print("Commands:")
        print("  add     - Add new manual content")
        print("  list    - List all manual content")
        print("  preview - Preview existing content")

