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
from datetime import datetime, timedelta, timezone
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

def get_optional_env_var(name):
    """Get an optional environment variable, returning None if not set."""
    return os.environ.get(name) or None

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

def parse_tag_command(subject):
    """
    Parse subject for tag/untag commands.
    Format: link: tag: <tag-name>: <url>
            link: untag: <tag-name>: <url>

    Returns (command, tag_name, url) or None if not a tag command.
    """
    if not subject:
        return None

    # Pattern: link: (tag|untag): <tag-name>: <url>
    pattern = re.compile(
        r'^\s*link:\s*(tag|untag):\s*([^:]+):\s*(.+?)\s*$',
        re.IGNORECASE
    )
    match = pattern.match(subject)
    if match:
        command = match.group(1).lower()  # 'tag' or 'untag'
        tag_name = match.group(2).strip()
        url = match.group(3).strip()
        return (command, tag_name, url)
    return None

def find_link_by_url(url, links_dir="content/links"):
    """
    Search all link markdown files for one containing the given URL.
    Returns the filepath if found, None otherwise.
    """
    if not os.path.exists(links_dir):
        return None

    for filename in os.listdir(links_dir):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(links_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Check if URL appears in the file (in params.url)
            if url in content:
                # Parse YAML to verify it's in params.url
                parts = content.split('---')
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter and frontmatter.get('params', {}).get('url') == url:
                        return filepath
        except Exception:
            continue
    return None

def modify_link_tags(filepath, command, tag_name):
    """
    Modify tags in a link markdown file.
    command: 'tag' to add, 'untag' to remove
    Returns True if modified, False otherwise.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    parts = content.split('---')
    if len(parts) < 3:
        return False

    frontmatter = yaml.safe_load(parts[1])
    if not frontmatter:
        return False

    tags = frontmatter.get('tags', [])
    if tags is None:
        tags = []

    modified = False
    if command == 'untag':
        if tag_name in tags:
            tags.remove(tag_name)
            modified = True
    elif command == 'tag':
        if tag_name not in tags:
            tags.append(tag_name)
            modified = True

    if modified:
        frontmatter['tags'] = tags
        yaml_content = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        new_content = f"---\n{yaml_content}---\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return modified

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
    recipient_email = get_optional_env_var("RECIPIENT_EMAIL")

    logger.info(f"Connecting to {imap_server} as {username}")
    if recipient_email:
        logger.info(f"Filtering by recipient: {recipient_email}")

    try:
        with MailBox(imap_server).login(username, password, initial_folder='INBOX') as mailbox:
            # Only process messages from the last 24 hours
            since_date = (datetime.now(timezone.utc) - timedelta(hours=24)).date()

            # Build criteria: UNSEEN messages from ALLOWED_SENDER within last 24 hours
            # Optionally filter by recipient email (useful for plus-addressing like foo+link@example.com)
            if recipient_email:
                criteria = AND(seen=False, from_=allowed_sender, to=recipient_email, date_gte=since_date)
            else:
                criteria = AND(seen=False, from_=allowed_sender, date_gte=since_date)

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
                    # Check if this is a tag command (link: tag: or link: untag:)
                    tag_cmd = parse_tag_command(msg.subject)
                    if tag_cmd:
                        command, tag_name, url = tag_cmd
                        logger.info(f"Processing tag command: {command} '{tag_name}' on {url}")

                        filepath = find_link_by_url(url)
                        if filepath:
                            if modify_link_tags(filepath, command, tag_name):
                                logger.info(f"Modified tags in {filepath}: {command} '{tag_name}'")
                            else:
                                logger.info(f"No change needed for {filepath}")
                        else:
                            logger.warning(f"No link found for URL: {url}")

                        mailbox.flag(msg.uid, '\\Seen', True)
                        continue

                    # Otherwise, process as a new link
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
