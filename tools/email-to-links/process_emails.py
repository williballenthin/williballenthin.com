# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "imap-tools",
#     "python-dateutil",
#     "pyyaml",
#     "beautifulsoup4",
# ]
# ///

import os
import re
import sys
import logging
import yaml
from datetime import datetime
from imap_tools import MailBox, AND
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_env_var(name):
    value = os.environ.get(name)
    if not value:
        logger.error(f"Environment variable {name} is not set.")
        sys.exit(1)
    return value

def clean_subject(subject):
    """
    Strips 'link:' case-insensitive prefix and whitespace.
    """
    if not subject:
        return "No Title"

    # Remove leading 'link:' (case insensitive) and whitespace
    pattern = re.compile(r'^\s*link:\s*', re.IGNORECASE)
    cleaned = pattern.sub('', subject).strip()
    return cleaned if cleaned else "No Title"

def extract_url_from_html(body):
    """
    Extract URL from HTML content, preferring href attributes in <a> tags.
    """
    try:
        soup = BeautifulSoup(body, 'html.parser')
        
        # Look for <a> tags with href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith(('http://', 'https://')):
                return href, str(soup)  # Return URL and parsed HTML as text
                
        # If no <a> tags found, convert to text and fallback to text parsing
        return None, soup.get_text()
    except:
        # If HTML parsing fails, return None and original body
        return None, body

def extract_url_and_tags(body):
    """
    Finds the first URL and hashtags near the URL in the body.
    Handles both HTML (with <a> tags) and plain text content.
    Only extracts tags that are preceded by whitespace or start of string,
    and only from the vicinity of the URL to avoid headers/signatures.
    """
    if not body:
        return None, []

    # First try to extract URL from HTML if it looks like HTML
    url = None
    text_body = body
    
    if '<' in body and '>' in body:
        html_url, text_body = extract_url_from_html(body)
        if html_url:
            url = html_url
    
    # If no URL found in HTML, try regex on the text content
    if not url:
        url_pattern = re.compile(r'(https?://[^\s]+)')
        url_match = url_pattern.search(text_body)
        url = url_match.group(1) if url_match else None

    if not url:
        return None, []

    # Find the position of the URL in the text body for tag extraction
    # Use the text version for tag extraction to avoid HTML noise
    url_position = text_body.find(url)
    if url_position == -1:
        # If exact URL not found in text, search for the domain part
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            url_position = text_body.find(domain)
        except:
            url_position = 0
    
    if url_position != -1:
        # Extract a reasonable window around the URL to look for tags
        window_size = 500
        start_pos = max(0, url_position - window_size)
        end_pos = min(len(text_body), url_position + len(url) + window_size)
        url_vicinity = text_body[start_pos:end_pos]
    else:
        # Fallback: search entire text body if URL position not found
        url_vicinity = text_body

    # Regex for hashtags that are preceded by whitespace or start of string
    tag_pattern = re.compile(r'(?:^|\s)#(\w+)')
    tags = tag_pattern.findall(url_vicinity)

    return url, tags

def generate_markdown_content(title, date_obj, url, tags):
    """
    Generates the markdown content with frontmatter using YAML serialization.
    """
    # Slug format: YYYYMMDDTHHMMSS
    slug = date_obj.strftime("%Y%m%dT%H%M%S")

    # Date format: ISO 8601 (YYYY-MM-DDTHH:MM:SS+HHMM)
    # We ensure it has timezone info. If not, assume UTC?
    # imap-tools usually returns timezone-aware datetimes.
    date_str = date_obj.isoformat()

    # Create frontmatter data structure
    frontmatter = {
        'title': title,
        'slug': slug,
        'date': date_str,
        'params': {
            'url': url
        },
        'tags': tags
    }

    # Serialize to YAML
    yaml_content = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    
    # Create final content with YAML frontmatter
    content = f"---\n{yaml_content}---\n"
    return slug, content

def main():
    imap_server = get_env_var("IMAP_SERVER")
    username = get_env_var("IMAP_USERNAME")
    password = get_env_var("IMAP_PASSWORD")
    allowed_sender = get_env_var("ALLOWED_SENDER")

    logger.info(f"Connecting to {imap_server} as {username}")

    try:
        with MailBox(imap_server).login(username, password, initial_folder='INBOX') as mailbox:
            # Fetch UNSEEN messages from ALLOWED_SENDER
            # We strictly filter by sender to avoid processing spam or other emails
            criteria = AND(seen=False, from_=allowed_sender)

            # Using fetch(mark_seen=False) initially to process first, then mark seen if successful?
            # Or just mark_seen=True (default is True in fetch unless specified otherwise, actually wait...
            # imap_tools fetch default mark_seen is True).
            # Let's verify documentation memory or assume safe default.
            # Usually it's better to read, process, then mark seen explicitly OR rely on fetch marking it.
            # If script crashes, we might lose the email state (marked read but not saved).
            # Safer: fetch(mark_seen=False), then loop, save file, then mailbox.flag(msg.uid, '\\Seen', True).

            messages = list(mailbox.fetch(criteria, mark_seen=False))
            logger.info(f"Found {len(messages)} new messages from {allowed_sender}")

            for msg in messages:
                try:
                    # 1. Parse Date
                    date_obj = msg.date
                    # Ensure timezone (msg.date from imap_tools is usually aware)

                    # 2. Parse Subject
                    title = clean_subject(msg.subject)

                    # 3. Parse Body
                    # Prefer plain text, fallback to html (stripped)
                    body = msg.text or msg.html
                    # If html, we might want to strip tags, but extraction regex might handle it.
                    # Simple approach: use msg.text if available.

                    url, tags = extract_url_and_tags(body)

                    if not url:
                        logger.warning(f"No URL found in email '{msg.subject}' from {msg.date}. Skipping.")
                        # We do NOT mark as seen, so we can retry or manually fix?
                        # Or do we mark as seen to avoid infinite loop of errors?
                        # User said "Scan all... mark as read".
                        # If we fail to extract, maybe we should still mark as read to clear the queue.
                        # Let's log and mark as seen.
                        mailbox.flag(msg.uid, '\\Seen', True)
                        continue

                    # 4. Generate Content
                    slug, content = generate_markdown_content(title, date_obj, url, tags)

                    # 5. Write File
                    output_dir = "content/links"
                    os.makedirs(output_dir, exist_ok=True)

                    filename = f"{output_dir}/{slug}.md"

                    # Check if file exists (collision)
                    counter = 1
                    while os.path.exists(filename):
                        logger.warning(f"File {filename} already exists. Appending counter to disambiguate.")
                        new_slug = f"{slug}_{counter}"
                        filename = f"{output_dir}/{new_slug}.md"
                        # We need to update the slug in the content too?
                        # Ideally yes, but frontmatter slug often used for URL.
                        # If we change filename, we should arguably change the frontmatter slug too to match.
                        content = content.replace(f"slug: {slug}", f"slug: {new_slug}")
                        counter += 1

                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)

                    logger.info(f"Created link: {filename}")

                    # 6. Mark as Seen
                    mailbox.flag(msg.uid, '\\Seen', True)

                except Exception as e:
                    logger.error(f"Error processing message uid={msg.uid}: {e}")
                    # We continue to next message

    except Exception as e:
        logger.error(f"IMAP connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
