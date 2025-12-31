# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "imap-tools",
#     "python-dateutil",
#     "pytest",
# ]
# ///

from datetime import datetime, timezone
import pytest

# Helper to import the script module which is in tools/email-to-links/process_emails.py
# Since it's a script not a module, we can import it if we add __init__.py or just use importlib.
# Given the directory structure 'tools/email-to-links', let's use importlib to load it
import importlib.util
import sys
import os

spec = importlib.util.spec_from_file_location("process_emails", "tools/email-to-links/process_emails.py")
process_emails_module = importlib.util.module_from_spec(spec)
sys.modules["process_emails"] = process_emails_module
spec.loader.exec_module(process_emails_module)

def test_clean_subject():
    assert process_emails_module.clean_subject("Link: Cool Article") == "Cool Article"
    assert process_emails_module.clean_subject("link:Cool Article") == "Cool Article"
    assert process_emails_module.clean_subject("LINK:   Cool Article  ") == "Cool Article"
    assert process_emails_module.clean_subject("Just a Subject") == "Just a Subject"
    assert process_emails_module.clean_subject("") == "No Title"

def test_extract_url_and_tags():
    # Basic URL + Tag
    body = "Check this: https://example.com #cool"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["cool"]

    # Multiple URLs (take first)
    body = "https://first.com and https://second.com"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://first.com"
    assert tags == []

    # Complex Tags
    body = "https://site.com #python #web_dev"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://site.com"
    assert tags == ["python", "web_dev"]

    # No URL
    body = "Just text #tag"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url is None
    assert tags == ["tag"]

    # No Tags
    body = "https://site.com"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://site.com"
    assert tags == []

def test_generate_markdown_content():
    title = "My Title"
    date_obj = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    url = "https://example.com"
    tags = ["one", "two"]

    slug, content = process_emails_module.generate_markdown_content(title, date_obj, url, tags)

    assert slug == "20240101T120000"
    assert "title: My Title" in content
    assert "slug: 20240101T120000" in content
    assert "date: 2024-01-01T12:00:00+00:00" in content
    assert "url: https://example.com" in content
    assert "- one" in content
    assert "- two" in content
