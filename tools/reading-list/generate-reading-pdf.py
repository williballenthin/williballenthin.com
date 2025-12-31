#!/usr/bin/env python3
# /// script
# dependencies = [
#  "feedparser",
#  "requests",
#  "beautifulsoup4",
# ]
# ///

"""
Generate a PDF reading list from RSS feed links for Remarkable 2.

This script:
1. Fetches the RSS feed from https://www.williballenthin.com/links/index.xml
2. Extracts permalinks from the RSS feed
3. Fetches each permalink page to find the actual target URL and tags
4. Filters by exclude tags
5. Uses percollate to generate an A4 PDF suitable for Remarkable 2

Requires:
- percollate (npm install -g percollate)
- Python 3 with feedparser, requests, beautifulsoup4
"""

import sys
import subprocess
import logging
import os
import requests
import feedparser
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import time

# Configure logger
logger = logging.getLogger(__name__)

# Define paths relative to the script location
HERE = Path(__file__).parent
ROOT = HERE.parent.parent
RSS_URL = "https://www.williballenthin.com/links/index.xml"

def get_target_url_and_tags(permalink):
    """
    Fetch the permalink page and extract the target URL and tags.
    Target URL is expected in <h1 id="title"><a href="...">...</a></h1>
    Tags are expected in <span class="link-tag"><a href="...">#tag</a></span>
    """
    try:
        response = requests.get(permalink, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract target URL
        title_h1 = soup.find('h1', id='title')
        if not title_h1:
            return None, []

        link = title_h1.find('a')
        if not link or not link.get('href'):
            return None, []

        target_url = link['href']

        # Extract tags
        tags = []
        # Look for tags in standard Hugo structure based on observed HTML
        # <span class="link-tag"><a href="...">#tag</a></span>
        tag_spans = soup.find_all('span', class_='link-tag')
        for span in tag_spans:
            a_tag = span.find('a')
            if a_tag:
                tag_text = a_tag.get_text(strip=True).lstrip('#')
                tags.append(tag_text)

        return target_url, tags

    except Exception as e:
        print(f"Error fetching {permalink}: {e}")
        return None, []

def get_rss_links(limit=10, exclude_tags=None):
    """
    Fetch RSS feed and return list of items with target URLs.
    """
    exclude_tags = exclude_tags or []
    items = []
    
    print(f"Fetching RSS feed from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)

    if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
        print(f"Warning: Error parsing RSS feed: {feed.bozo_exception}")

    print(f"Found {len(feed.entries)} entries in RSS feed.")

    processed_count = 0

    for entry in feed.entries:
        if len(items) >= limit:
            break

        processed_count += 1
        title = entry.title
        permalink = entry.link
        
        # Parse date
        published = entry.published_parsed
        if published:
            date_val = datetime.fromtimestamp(time.mktime(published))
        else:
            date_val = datetime.now()
            
        print(f"Processing [{processed_count}]: {title}")

        target_url, tags = get_target_url_and_tags(permalink)

        if not target_url:
            print(f"  Skipping: Could not find target URL for {permalink}")
            continue

        # Check exclusions
        if exclude_tags and any(tag in exclude_tags for tag in tags):
            print(f"  Skipping: Excluded tag found (tags: {tags})")
            continue

        items.append({
            'title': title,
            'url': target_url,
            'date': date_val,
            'tags': tags,
            'permalink': permalink
        })

        # Be nice to the server
        time.sleep(0.1)

    print(f"Found {len(items)} valid items.")
    return items

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
        '--css', '@page { size: A4; margin: 0.5cm }',
        '--title', f'Reading List - {datetime.now().strftime("%Y-%m-%d")}',
        '--author', 'williballenthin via RSS',
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

            # Check file size
            try:
                size_bytes = os.path.getsize(output_path)
                size_mb = size_bytes / (1024 * 1024)
                print(f"Output file size: {size_mb:.2f} MB")
            except OSError:
                print("Could not determine output file size")

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
    logging.basicConfig(level=logging.INFO)
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
        
        print(f"Generating reading list with {num_articles} articles from RSS")
        if exclude_tags:
            print(f"Excluding articles with tags: {', '.join(exclude_tags)}")
        
        # Fetch RSS links
        urls = get_rss_links(num_articles, exclude_tags)
        
        if not urls:
            print("No URLs found in RSS feed")
            return 1
        
        # Print what we found
        print("\nArticles to include:")
        for i, item in enumerate(urls, 1):
            logger.info(f"Article chosen: {item['title']}")
            print(f"{i:2}. {item['title']}")
            print(f"    {item['url']}")
            print(f"    Date: {item['date']}")
            if item['tags']:
                print(f"    Tags: {', '.join(item['tags'])}")
        
        # Generate PDF
        success = generate_pdf(urls, output_file)
        
        if success:
            size = os.path.getsize(output_file)
            logger.info(f"Generated PDF size: {size} bytes")
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
