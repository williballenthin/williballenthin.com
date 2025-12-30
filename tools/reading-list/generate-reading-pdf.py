#!/usr/bin/env python3
"""
Generate a PDF reading list from Pinboard RSS feed for Remarkable 2.

This script:
1. Fetches the latest entries from the Pinboard RSS feed
2. Extracts the top N URLs
3. Uses percollate to generate an A4 PDF suitable for Remarkable 2

Requires:
- percollate (npm install -g percollate)
- Python 3 with standard library
"""

import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import sys
import json
import subprocess
import tempfile
import os
from datetime import datetime


def fetch_pinboard_rss(username="williballenthin"):
    """Fetch the RSS feed from Pinboard."""
    url = f"https://feeds.pinboard.in/rss/u:{username}/"
    print(f"Fetching RSS feed from {url}")
    
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')


def parse_rss_urls(rss_content, limit=10, exclude_tags=None):
    """Parse RSS content and extract URLs with metadata."""
    exclude_tags = exclude_tags or []
    root = ET.fromstring(rss_content)
    
    # Handle RSS 1.0 format (what Pinboard uses)
    items = []
    
    # Find all item elements
    for item in root.findall('.//{http://purl.org/rss/1.0/}item'):
        title_elem = item.find('.//{http://purl.org/rss/1.0/}title')
        link_elem = item.find('.//{http://purl.org/rss/1.0/}link')
        desc_elem = item.find('.//{http://purl.org/rss/1.0/}description')
        subject_elem = item.find('.//{http://purl.org/dc/elements/1.1/}subject')
        
        # Extract tags
        tags = []
        if subject_elem is not None and subject_elem.text:
            tags = [tag.strip() for tag in subject_elem.text.split()]
        
        # Check if any excluded tags are present
        if exclude_tags and any(tag in exclude_tags for tag in tags):
            continue
        
        if link_elem is not None:
            url = link_elem.text
            title = title_elem.text if title_elem is not None else url
            description = desc_elem.text if desc_elem is not None else ""
            
            items.append({
                'url': url,
                'title': title,
                'description': description,
                'tags': tags
            })
    
    print(f"Found {len(items)} items in RSS feed (after filtering)")
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
        
        # Fetch and parse RSS
        rss_content = fetch_pinboard_rss()
        urls = parse_rss_urls(rss_content, num_articles, exclude_tags)
        
        if not urls:
            print("No URLs found in RSS feed after filtering")
            return 1
        
        # Print what we found
        print("\nArticles to include:")
        for i, item in enumerate(urls, 1):
            print(f"{i:2}. {item['title']}")
            print(f"    {item['url']}")
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
