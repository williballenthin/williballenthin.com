#!/usr/bin/env python3
"""
Generate a PDF reading list from local link Markdown files for Remarkable 2.

This script:
1. Scans the local 'content/links' directory for Markdown files
2. Extracts metadata (title, url, date, tags) from frontmatter
3. Sorts by date descending
4. Extracts the top N URLs
5. Uses percollate to generate an A4 PDF suitable for Remarkable 2

Requires:
- percollate (npm install -g percollate)
- Python 3 with standard library
"""

import sys
import subprocess
import os
import glob
import re
from pathlib import Path
from datetime import datetime, timezone

# Define paths relative to the script location
HERE = Path(__file__).parent
ROOT = HERE.parent.parent
LINKS_DIR = ROOT / "content" / "links"

def parse_frontmatter(content):
    """
    Parse simple YAML frontmatter using regex to avoid external dependencies.
    Extracts title, date, url, and tags.
    """
    # Extract the frontmatter block
    # Robustly split by '---'
    parts = content.split('---')
    if len(parts) < 3:
        return None
    
    fm_text = parts[1]

    # Extract fields
    title_match = re.search(r'^title:\s*(.+)$', fm_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    date_match = re.search(r'^date:\s*(.+)$', fm_text, re.MULTILINE)
    date_str = date_match.group(1).strip() if date_match else None

    # URL is usually nested under params
    url_match = re.search(r'^\s+url:\s*(.+)$', fm_text, re.MULTILINE)
    url = url_match.group(1).strip() if url_match else None

    # Fallback if url is top-level (unlikely based on known structure but safe to have)
    if not url:
        top_url_match = re.search(r'^url:\s*(.+)$', fm_text, re.MULTILINE)
        if top_url_match:
            url = top_url_match.group(1).strip()

    # Extract tags
    tags = []
    # Find the tags block
    tags_match = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n)+)', fm_text, re.MULTILINE)
    if tags_match:
        tag_lines = tags_match.group(1).strip().split('\n')
        for line in tag_lines:
            tag_match = re.search(r'^\s*-\s*(.+)$', line)
            if tag_match:
                tags.append(tag_match.group(1).strip())

    # Parse date
    date_val = datetime.min.replace(tzinfo=timezone.utc)
    if date_str:
        try:
            # Handle potential quotes
            date_str = date_str.strip('"\'')
            date_val = datetime.fromisoformat(date_str)
        except ValueError:
            print(f"Warning: could not parse date {date_str}")

    return {
        'title': title,
        'url': url,
        'date': date_val,
        'tags': tags
    }

def get_local_links(limit=10, exclude_tags=None):
    """
    Scan content/links directory and return sorted list of items.
    """
    exclude_tags = exclude_tags or []
    items = []
    
    if not LINKS_DIR.exists():
        print(f"Error: Links directory not found at {LINKS_DIR}")
        return []
        
    print(f"Scanning files in {LINKS_DIR}...")

    files = list(LINKS_DIR.glob("*.md"))
    print(f"Found {len(files)} markdown files.")

    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8')
            meta = parse_frontmatter(content)

            if not meta or not meta['url']:
                continue

            # Check exclusions
            if exclude_tags and any(tag in exclude_tags for tag in meta['tags']):
                continue

            items.append(meta)
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            
    # Sort by date descending
    items.sort(key=lambda x: x['date'], reverse=True)

    print(f"Found {len(items)} valid items (after filtering)")
    return items[:limit]

def generate_pdf(urls, output_path="reading-list.pdf"):
    """Use percollate to generate A4 PDF from URLs."""
    if not urls:
        print("No URLs to process")
        return False
    
    print(f"Generating PDF with {len(urls)} articles...")
    
    # Prepare percollate command
    cmd = [
        'percollate', 'pdf',
        '--no-sandbox',  # Required for running as root
        '--output', output_path,
        '--css', '@page { size: A4; margin: 2cm }',
        '--title', f'Reading List - {datetime.now().strftime("%Y-%m-%d")}',
        '--author', 'williballenthin via Pinboard',
        '--toc',  # Generate table of contents
        '--wait', '2'  # Be nice to servers
    ]
    
    # Add URLs
    for item in urls:
        cmd.append(item['url'])
    
    print(f"Running: {' '.join(cmd[:8])}... [{len(urls)} URLs]")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"Successfully generated PDF: {output_path}")
            return True
        else:
            print(f"Error generating PDF: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("PDF generation timed out")
        return False
    except Exception as e:
        print(f"Error running percollate: {e}")
        return False

def main():
    try:
        # Parse command line arguments
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
            print("Usage: python generate-reading-pdf.py [num_articles] [output_file] [--exclude-tags tag1,tag2,...]")
            print("  num_articles: Number of articles to include (default: 10)")
            print("  output_file: Output PDF filename (default: reading-list.pdf)")
            print("  --exclude-tags: Comma-separated list of tags to exclude (e.g., 'read,archived')")
            return 0
        
        # Configuration
        num_articles = 10
        output_file = "reading-list.pdf"
        exclude_tags = []
        
        # Parse arguments
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--exclude-tags' and i + 1 < len(sys.argv):
                exclude_tags = [tag.strip() for tag in sys.argv[i + 1].split(',')]
                i += 2
            elif arg.startswith('--exclude-tags='):
                exclude_tags = [tag.strip() for tag in arg.split('=', 1)[1].split(',')]
                i += 1
            elif i == 1 and arg.isdigit():
                num_articles = int(arg)
                i += 1
            elif i == 2 or (i == 1 and not arg.isdigit()):
                output_file = arg
                i += 1
            else:
                print(f"Unknown argument: {arg}")
                return 1
        
        print(f"Generating reading list with {num_articles} articles")
        if exclude_tags:
            print(f"Excluding articles with tags: {', '.join(exclude_tags)}")
        
        # Fetch local links
        urls = get_local_links(num_articles, exclude_tags)
        
        if not urls:
            print("No URLs found in content/links")
            return 1
        
        # Print what we found
        print("\nArticles to include:")
        for i, item in enumerate(urls, 1):
            print(f"{i:2}. {item['title']}")
            print(f"    {item['url']}")
            print(f"    Date: {item['date']}")
            if item['tags']:
                print(f"    Tags: {', '.join(item['tags'])}")
        
        # Generate PDF
        success = generate_pdf(urls, output_file)
        
        if success:
            print(f"\nSuccess! PDF generated: {output_file}")
            return 0
        else:
            print("\nFailed to generate PDF")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
