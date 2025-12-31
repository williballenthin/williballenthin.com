# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "imap-tools",
#     "python-dateutil",
# ]
# ///

import os
import re
import sys
import logging
from datetime import datetime
from imap_tools import MailBox, AND

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

def extract_url_and_tags(body):
    """
    Finds the first URL and all hashtags in the body.
    """
    if not body:
        return None, []

    # Regex for URL (simple http/https)
    # Matches http/s followed by non-whitespace characters
    url_pattern = re.compile(r'(https?://[^\s]+)')
    url_match = url_pattern.search(body)
    url = url_match.group(1) if url_match else None

    # Regex for hashtags
    # Matches # followed by word characters (alphanumeric + underscore)
    # Excludes hashtags that might be part of a URL fragment if not careful,
    # but generally #tag is distinct.
    # Note: URL regex is greedy for non-whitespace, so tags usually aren't inside the URL match
    # unless it's an anchor, but usually anchors don't look like '#tag ' with space.
    # We scan the whole body for tags.
    tag_pattern = re.compile(r'#(\w+)')
    tags = tag_pattern.findall(body)

    return url, tags

def generate_markdown_content(title, date_obj, url, tags):
    """
    Generates the markdown content with frontmatter.
    """
    # Slug format: YYYYMMDDTHHMMSS
    slug = date_obj.strftime("%Y%m%dT%H%M%S")

    # Date format: ISO 8601 (YYYY-MM-DDTHH:MM:SS+HHMM)
    # We ensure it has timezone info. If not, assume UTC?
    # imap-tools usually returns timezone-aware datetimes.
    date_str = date_obj.isoformat()

    # Clean tags
    tag_list = "\n".join([f"- {tag}" for tag in tags])

    content = f"""---
title: {title}
slug: {slug}
date: {date_str}
params:
  url: {url}
tags:
{tag_list}
---
"""
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
